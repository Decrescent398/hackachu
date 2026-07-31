import scrapy
import numpy
import json

# from setup import sets

class PokeSpider(scrapy.Spider):
    name = 'poke'
    sets = ['Brilliant Stars', 'Vivid Voltage', 'Celebrations' 'Astral Radiance', 'Lost Origin', 'Silver Tempest', 'Crown Zenith', 'Scarlet & Violet', 'Paldea Evolved', 'Obsidian Flames', 'Scarlet & Violet' 'Paradox Rift']
    start_urls = ['https://www.digitaltq.com/' + pokeset.replace(' ', '-') + '-pull-rates-pokemon-tcg' for pokeset in sets]

    def parse(self, response):
        table = response.css('div.table-responsive')
        
        data = numpy.array(table.css('td::text').getall())
        data = data.reshape(int(len(data) / 3), 3)
        data = numpy.delete(data, 1, axis=1)
        
        print(data)