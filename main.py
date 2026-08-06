import pandas as pd

sets = ['Brilliant Stars', 'Lost Origin', 'Silver Tempest', 'Crown Zenith', 'Paldea Evolved', 'Obsidian Flames']

cards = pd.read_csv('pokemon-tcg-data-master-1999-2023.csv')
scraped = pd.read_json('pull_rates.json', lines=True)

cards = cards[cards['set'].isin(sets)]
cards['rarity'] = cards['rarity'].replace('Ultra Rare', 'Rare Ultra')

scraped['rarity'] = scraped['rarity'].replace('Secret Rare Holo', 'Rare Secret')
scraped['rarity'] = scraped['rarity'].replace('Ultra Rare', 'Rare Ultra') 
scraped['rarity'] = scraped['rarity'].replace('Rare Radiant', 'Radiant Rare') 
scraped['rarity'] = scraped['rarity'].replace('Double Rare Holo', 'Double Rare') 

for setnum in range(len(sets)):
    
    scraped_card_types = dfg.loc[dfg['set'] == sets[setnum], ['rarity']]
    scraped_rarities = sorted(set(scraped_card_types['rarity']))
    
    card_types = cards.loc[cards['set'] == sets[setnum], ['rarity']]
    all_types = scraped_rarities + sorted(set(card_types['rarity']))
    
    for ctype in all_types:
        if ctype not in scraped_rarities:
            dfg.loc[len(dfg)] = [sets[setnum], ctype, (len(card_types.loc[card_types['rarity'] == ctype]) / len(card_types))]
            
x = pd.merge(cards, scraped, on=['set','rarity'], how='inner')

for setnum in range(len(sets)):
    
    all_rarities = sorted(set(cards.loc[cards['set'] == sets[setnum], ['rarity']]['rarity']))
    
    for rarity in all_rarities:
        
        total_cards_of_rarity = len(x.loc[(x['set'] == sets[setnum]) & (x['rarity'] == rarity), 'rarity'])
        pull_rate = dfg.loc[(dfg['set'] == sets[setnum]) & (dfg['rarity'] == rarity), 'pullRate']
        
        x.loc[(x['set'] == sets[setnum]) & (x['rarity'] == rarity), 'pullRate'] = (1/total_cards_of_rarity) * pull_rate.item()