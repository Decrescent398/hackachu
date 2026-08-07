import pandas as pd

sets = ['Brilliant Stars', 'Lost Origin', 'Silver Tempest', 'Crown Zenith', 'Paldea Evolved', 'Obsidian Flames']

cards = pd.read_csv('pokemon-tcg-data-master-1999-2023.csv')
scraped = pd.read_json('pull_rates.json', lines=True)

cards = cards[cards['set'].isin(sets)]
cards['rarity'] = cards['rarity'].replace('Ultra Rare', 'Rare Ultra')

scraped['rarity'] = scraped['rarity'].replace({
    'Secret Rare Holo': 'Rare Secret',
    'Ultra Rare': 'Rare Ultra',
    'Rare Radiant': 'Radiant Rare',
    'Double Rare Holo': 'Double Rare'}) 

card_rarity_count = cards.groupby(['set', 'rarity']).size().rename('n').reset_index()

card_rarity_count['total'] = card_rarity_count.groupby('set')['n'].transform('sum')
card_rarity_count['pullRate'] = card_rarity_count['n'] / card_rarity_count['total']

present = scraped.set_index(['set', 'rarity']).index
missing = card_rarity_count[~card_rarity_count.set_index(['set', 'rarity']).index.isin(present)][['set', 'rarity', 'pullRate']]

scraped = pd.concat([scraped, missing], ignore_index=True)
            
x = pd.merge(cards, scraped, on=['set','rarity'], how='inner')

x['groupPullRate'] = x.groupby(['set', 'rarity'])['pullRate'].transform('first')
x['countInGroup'] = x.groupby(['set', 'rarity'])['rarity'].transform('count')
x['pullRate'] = x['groupPullRate'] / x['countInGroup']