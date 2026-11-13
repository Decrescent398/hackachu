import scrapy
import json
import numpy as np

root = "https://www.thepricedex.com"

special_sets = {
    
    "unlimited": [ # 2 pull rate tabs (regular, unlimited)
        "neo-destiny",
        "neo-revelation",
        "neo-discovery",
        "neo-genesis",
        "gym-challenge",
        "gym-heroes",
        "team-rocket",
        "fossil",
        "jungle",
        ],

    "shadowless": [ # 3 pull rate tabs (regular, unlimited, shadowless)
        "base-set",
        ],

    "nobooster": [ # No Booster Box tab
        "30th-celebration",
        "ascended-heroes",
        "black-bolt",
        "white-flare",
        "prismatic-evolutions",
        "shrouded-fable",
        "paldean-fates",
        "151",
        "crown-zenith",
        "pokemon-go",
        "celebrations",
        "shining-fates",
        "champions-path",
        "hidden-fates",
        "detective-pikachu",
        "dragon-majesty",
        "shining-legends",
        "generations",
        "double-crisis",
        "dragon-vault",
        ],
}

class PokeSpider(scrapy.Spider):
    
    name = "poke"
    start_urls = [root+"/sets"]

    def parse(self, response):
        setdirs = response.css("div.MuiBox-root.css-0 a::attr(href)").getall()
        
        setdirs = [root+setdir for setdir in setdirs if "set/" in setdir]
        for setdir in [setdirs[1]]: # Newest sets likely don't have pull rates posted yet 
            yield response.follow(setdir, callback=self.parse_details)
            
    def parse_details(self, response):
        details = {
            "logo": response.css("div.MuiBox-root.css-1kbd6lt img::attr(src)").get(),
            "name": response.css("div.MuiBox-root.css-0 h1::text").get(),
            "Cards in Set": list(float(i) for i in 
                             "".join(response.css("div.MuiBox-root.css-i8nfdw span::text").getall()).split()
                             if i.isdigit())[0],
            "Variants in Set": list(float(i) for i in 
                             "".join(response.css("div.MuiBox-root.css-i8nfdw span::text").getall()).split()
                             if i.isdigit())[1],
            **dict(zip(
                    ("Release Date", "No. of Cards", "Set Code", "Set Group"), 
                    list(i.split(": ")[-1].split(" Cards")[0] for i in 
                         response.css("div.MuiStack-root.css-1xrn837 span::text").getall()),
            )),
            "Card Rarities": {
                tier: {
                    "Count": tier_count,
                    "Rarities": {k: {"Count": float(v)} for k,v in 
                                list(i.split(": ") for i in 
                                     rarities.css("span.MuiChip-label::text").getall())
                                },
                    }
                for tier, tier_count, rarities in
                zip(
                    list(i.replace("(", "").replace(")", "").strip() for i in
                        response.css("div.MuiBox-root.css-1rr4qq7 span::text").getall() 
                        if "Cards" in i),
                    list(float(i.replace("(", "").replace(")", "").strip()) for i in 
                        response.css("div.MuiBox-root.css-1rr4qq7 span::text").getall() 
                        if i.strip().replace("(", "").replace(")", "").isdigit()),
                    response.css("div.MuiStack-root.css-1q13opc"),
                    )
                },
            "Cards": {
                num: {
                    "Name": name,
                    "Rarity": rarity,
                    "image": image,
                    "price": {cardtype: cardprice for cardtype, cardprice in
                              zip(
                                  list(i.strip() for i in 
                                       price.css("p.css-ggah30 b::text").getall()
                                       if i != ":"),
                                  list(float(i.replace("$", "").replace(",", "").strip()) for i in 
                                       price.css("p.css-ggah30::text").getall()
                                       if "$" in i),
                            )
                        },
                } 
                for num, name, rarity, image, price in
                zip(
                    list(i for i in 
                         response.css("p.css-10ao1mw::text").getall()
                         if i.isdigit()),
                    response.css("h6.css-1xoqslx::text").getall(),
                    response.css("span.css-b9zgoq::text").getall(),
                    list(f"https://images.scrydex.com/pokemon/{response.url.split("/")[-2]}-{i}/large" for i in 
                         response.css("p.css-10ao1mw::text").getall()
                         if i.isdigit()),
                    response.css("div.css-8eauar"),
                )
            },
            }
        
        if response.url.split("/")[-1] in special_sets["shadowless"]+special_sets["unlimited"]:
            prices = response.css("div.MuiBox-root.css-fku9wg p::text").getall()
            prices = prices[:int(len(prices)/2)]
            details["Set Value"] = {edition.replace("(", "").replace(")", "").strip(): float(price.replace("$", "").replace(",", ""))
                                    for edition, price in
                                    zip(prices[1::2], prices[::2])}
        else:
            details["Set Value"] = float(str(response.css("h5.MuiTypography-h5::text").get()).replace("$", "").replace(",", ""))
        
        nobooster = False
        if response.url.split("/")[-1] in special_sets["nobooster"]:
            nobooster = True
        
        yield response.follow(response.url+"/pull-rates", callback=self.parse_pullrates, cb_kwargs={"details": details, "nobooster": nobooster}) # cb_kwargs is passed into callback as a keyword argument
        
    def parse_pullrates(self, response, details, nobooster):
        
        details["Pull Rates Source"] = response.css("div.MuiBox-root.css-4sywta a::attr(href)").get()
        
        tables = response.css("div.MuiTableContainer-root")
        pull_rates_tables = tables[::2]
        expected_value_tables = tables[1::2]
        
        def clean_pull_rate_types(s):
            try:
                return s[s.strip().index("(") + 1: -1]
            except ValueError:
                return "Default"
        pull_rate_types = list(clean_pull_rate_types(i) 
                               for i in 
                               response.css("div.css-3bunz4 h2::text").getall())
        
        pull_rate_summary_titles = list(tuple(response.css("div.css-eo1dsv p::text").getall()[i: i+4]) 
                                        for i in range(0, len(response.css("div.css-eo1dsv p::text").getall()), len(pull_rate_types)))
        pull_rate_summary_values = list(tuple(response.css("div.css-eo1dsv h5::text").getall()[i: i+4]) 
                                        for i in range(0, len(response.css("div.css-eo1dsv h5::text").getall()), len(pull_rate_types)))
        
        for pull_rates_table, expected_value_table, pull_rate_type, \
                pull_rate_summary_title, pull_rate_summary_value in zip(
            pull_rates_tables, expected_value_tables, pull_rate_types, \
                pull_rate_summary_titles, pull_rate_summary_values):
            
            # <-- Pull Rates -->
            # (n)
            pull_rates_values = np.array(pull_rates_table.css("p::text").getall())
            
            if nobooster:
                cards_in_pack = float(pull_rates_values[-1].split()[0])
                cards_in_booster = 0.0
            else:
                cards_in_pack = float(pull_rates_values[-2].split()[0])
                cards_in_booster = float(pull_rates_values[-1].split()[0])
            
            idx = np.where(pull_rates_values == "Total")[0][0]
            pull_rates_values = pull_rates_values[:idx]
            
            if nobooster:
                cols = 3
            else:
                cols = 4
            
            # (n) -> (n/cols, cols)
            pull_rates_values = np.reshape(pull_rates_values, (int(len(pull_rates_values)/cols), cols))
            
            def convert_pull_rates(val):
                if "in" in val: # cols Pull Rate and Specific Card Odds
                    num = val.split()[2].replace(",", "")
                    return 1.0/ float(num)
                elif "cards per pack" or "card per pack" in val: # col Pull Rate
                    return float(val.split()[0])
                elif "cards" in val: # col Per Booster Box
                    return float(val.split(0))
                return np.nan
            
            vfunc = np.vectorize(convert_pull_rates, otypes=[float])
            rates = vfunc(pull_rates_values[:, list(i for i in range(1, cols))])
            pull_rates_values[:, list(i for i in range(1, cols))] = rates
            
            # (n/cols, cols) -> (n/cols, cols-1)
            pull_rates_values = np.delete(pull_rates_values, 0, axis=1) # delete str col
            pull_rates_values = pull_rates_values.astype(float)
            
            # <--- Expected Value --->
            # (n)
            expected_values = np.array(list(i.replace("$", "").replace(",", "").replace("—", "0") 
                                            for i in expected_value_table.css("p::text").getall()))
            
            total_priced = float(expected_values[-2])
            expected_value_per_pack = float(expected_values[-1])
            
            idx = np.where(expected_values == "Total")[0][0]
            expected_values = expected_values[:idx]
            
            # (n) -> (n/5, 5)
            expected_values = np.reshape(expected_values, (int(len(expected_values)/5), 5))
            # (n/5, 5) -> (n/4, 4)
            expected_values = np.delete(expected_values, 1, axis=1)
            
            # (n/4, 4) -> (n/4, 3)
            expected_values = np.delete(expected_values, 0, axis=1)
            expected_values = expected_values.astype(float)

            # <--- Common --->
            details.setdefault("Cards in Pack", {})[pull_rate_type] = cards_in_pack
            details.setdefault("Cards in Booster", {})[pull_rate_type] = cards_in_booster
            details.setdefault("Total Priced", {})[pull_rate_type] = total_priced
            details.setdefault("Expected Value Per Pack", {})[pull_rate_type] = expected_value_per_pack
            
            pull_rates = np.concatenate((pull_rates_values, expected_values), axis=1)
            
            start = 0
            for tier_key, tier_value in details["Card Rarities"].items():
                stop = start + len(tier_value["Rarities"].keys())
                pull_rates_clip = pull_rates[start: stop]
                start = stop
                
                for rarity, rarity_pull_rate_details in zip(
                    tier_value["Rarities"].keys(), pull_rates_clip,
                ):
                    details["Card Rarities"][tier_key]["Rarities"][rarity][pull_rate_type] = dict(zip(
                        (
                            "Pull Rate", "Cards Per Booster Box", "Specific Card Odds",
                            "Priced", "Average Value", "Expected Value Per Pack",
                        ),
                        rarity_pull_rate_details.tolist(),
                    ))
                
            for title, val in zip(
                pull_rate_summary_title, pull_rate_summary_value):
                clean_val = float(val.replace("$", "").replace(",", "").replace("—", "0"))
                details.setdefault(title, {})[pull_rate_type] = clean_val
        
        print(details)