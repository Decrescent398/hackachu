cards = pd.read_csv('pokemon-tcg-data-master-1999-2023.csv')
scraped = pd.read_json('pull_rates.json', lines=True)


scraped['rarity'] = scraped['rarity'].replace('Secret Rare Holo', 'Rare Secret')
scraped['rarity'] = scraped['rarity'].replace('Ultra Rare', 'Rare Ultra') 
cards['rarity'] = cards['rarity'].replace('Ultra Rare', 'Rare Ultra')

scraped['rarity'] = scraped['rarity'].replace('Rare Radiant', 'Radiant Rare') 

scraped['rarity'] = scraped['rarity'].replace('Double Rare Holo', 'Double Rare') 


