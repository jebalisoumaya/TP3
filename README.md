# TP3

SNCB Web Scraping Project - README
Overview
This project collects data from Belgian company registries using Scrapy spiders. It extracts information from the KBO (Kruispuntbank van Ondernemingen) database and the Belgian Official Journal (ejustice).

Project Structure
SNCB - Root project directory
SNCB/spiders/ - Directory containing spiders
kbospider.py - Spider for KBO data
ejusticespider.py - Spider for Belgian Official Journal data
data.json - Output file containing scraped KBO data
ejusticteste.json - Output file containing scraped ejustice data
enterprise.csv - Input file with enterprise numbers
Requirements
Python 3.7+
Scrapy
pymongo (optional, for MongoDB integration)


#Installation
#How to Run the KBO Spider
The KBO spider extracts company information from the Kruispuntbank van Ondernemingen.

scrapy crawl kbo -o data.json

# Run the spider
scrapy crawl ejustice -o ejustice_data.json



