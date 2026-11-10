import scrapy
from colorama import Fore, Style

colprint = lambda col, text: print(col + str(text) + Style.RESET_ALL)
root = "https://www.thepricedex.com/sets"

class PokeSpider(scrapy.Spider):
    
    name = "poke"
    start_urls = [root]

    def parse(self, response):
        data = response.css("div.MuiBox-root.css-0")
        sets = data.css("div.MuiBox-root.css-14880k0::attr(id)").getall()
        setdirs = data.css("a::attr(href)").getall()
        print(setdirs)