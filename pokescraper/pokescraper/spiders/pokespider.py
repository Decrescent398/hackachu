import scrapy
import json
import numpy as np

root = "https://www.thepricedex.com"

class PokeSpider(scrapy.Spider):
    
    name = "poke"
    start_urls = [root+"/sets"]

    def parse(self, response):
        setdirs = response.css("div.MuiBox-root.css-0 a::attr(href)").getall()
        
        setdirs = [root+setdir for setdir in setdirs if "set/" in setdir]
        for setdir in [setdirs[2]]: # Newest sets likely don't have pull rates posted yet 
            yield response.follow(setdir, callback=self.parse_details)
            
    def parse_details(self, response):
        details = {
            "logo": response.css("div.MuiBox-root.css-1kbd6lt img::attr(src)").get(),
            "name": response.css("div.MuiBox-root.css-0 h1::text").get(),
            **dict(zip(
                    ("Release Date", "No. of Cards", "Set Code", "Set Group"), 
                    list(i.split(": ")[-1].split(" Cards")[0] for i in 
                         response.css("div.MuiStack-root.css-1xrn837 span::text").getall()),
                )),
            "Card Rarities": {
                tier: {
                    "Count": tier_count,
                    "Rarities": {k: {"Count": int(v)} for k,v in 
                                list(i.split(": ") for i in 
                                     rarities.css("span.MuiChip-label::text").getall())
                            }
                    }
                for tier, tier_count, rarities in
                zip(
                    list(i.replace("(", "").replace(")", "").strip() for i in
                        response.css("div.MuiBox-root.css-1rr4qq7 span::text").getall() 
                        if "Cards" in i),
                    list(int(i.replace("(", "").replace(")", "").strip()) for i in 
                        response.css("div.MuiBox-root.css-1rr4qq7 span::text").getall() 
                        if i.strip().replace("(", "").replace(")", "").isdigit()),
                    response.css("div.MuiStack-root.css-1q13opc"),
                    )
                },
            "Cards": {}
            }
        yield response.follow(response.url+"/pull-rates", callback=self.parse_pullrates, cb_kwargs={"details": details}) # cb_kwargs is passed into callback as a keyword argument
        
    def parse_pullrates(self, response, details):
        
        tables = response.css("div.MuiTableContainer-root")
        pull_rates_table = tables[0]
        expected_value_table = tables[1]
        
        # (n)
        pull_rates_values = np.array(pull_rates_table.css("p::text").getall())
        
        cards_in_pack = float(pull_rates_values[-2].split()[0])
        cards_in_booster = float(pull_rates_values[-1].split()[0])
        
        idx = np.where(pull_rates_values == "Total")[0][0]
        pull_rates_values = pull_rates_values[:idx]
        
        # (n) -> (n/4, 4)
        pull_rates_values = np.reshape(pull_rates_values, (int(len(pull_rates_values)/4), 4))
        
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
        rates = vfunc(pull_rates_values[:, [1, 2, 3]])
        pull_rates_values[:, [1, 2, 3]] = rates
        
        # (n/4, 4) -> (n/4, 3)
        pull_rates_values = np.delete(pull_rates_values, 0, axis=1)
        pull_rates_values = pull_rates_values.astype(float)
        
        # (n)
        expected_values = np.array([i.replace("$", "").replace("—", "0") for i in expected_value_table.css("p::text").getall()])
        
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
        
        details["Cards in Pack"] = cards_in_pack
        details["Cards in Booster"] = cards_in_booster
        details["Total Priced"] = total_priced
        details["Expected Value Per Pack"] = expected_value_per_pack
        
        pull_rates = np.concatenate((pull_rates_values, expected_values), axis=1)
        
        start = 0
        for tier_key, tier_value in details["Card Rarities"].items():
            stop = start + len(tier_value["Rarities"].keys())
            pull_rates_clip = pull_rates[start: stop]
            start = stop
            
            for rarity, rarity_pull_rate_details in zip(
                tier_value["Rarities"].keys(), pull_rates_clip,
            ):
                details["Card Rarities"][tier_key]["Rarities"][rarity].update(dict(zip(
                    (
                        "Pull Rate", "Cards Per Booster Box", "Specific Card Odds",
                        "Priced", "Average Value", "Expected Value Per Pack",
                     ),
                    rarity_pull_rate_details.tolist(),
                )))
        
        print(details)