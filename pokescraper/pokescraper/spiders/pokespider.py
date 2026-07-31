import scrapy
import numpy
import json

# from setup import sets

green = '\033[32m'
reset = '\033[0m'

class PokeSpider(scrapy.Spider):
    
    name = 'poke'
    sets = ['Brilliant Stars', 'Lost Origin', 'Silver Tempest', 
                'Crown Zenith', 'Paldea Evolved', 'Obsidian Flames']
    start_urls = ['https://www.digitaltq.com/' 
                    + pokeset.replace(' ', '-') 
                    + '-pull-rates-pokemon-tcg' 
                    for pokeset in sets]

    def parse(self, response):
        setname = response.css('div.card-body h1.card-title::text').get().split('Pull')[0]
        
        table = response.css('div.table-responsive')
        
        data = numpy.array(table.css('td::text').getall())
        data = data.reshape(int(len(data) / 3), 3)
        data = numpy.delete(data, 1, axis=1)
        
        for row in data:
            rarity, pull_rate = row
            values = {
                "set": setname,
                "rarity": rarity,
                "pull_rate": pull_rate
            }
            with open('../pull_rates.json', 'a') as f:
                f.write(json.dumps(values) + '\n')