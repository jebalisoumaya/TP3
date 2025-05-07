import scrapy
import csv
import logging
from ..items import KboItem

class KboSpider(scrapy.Spider):
    name = "kbo"
    allowed_domains = ["kbopub.economie.fgov.be"]

    def __init__(self, csv_file=None, limit=10, *args, **kwargs):
        super(KboSpider, self).__init__(*args, **kwargs)
        if csv_file is None:
            csv_file = 'enterprise.csv'
        self.csv_file = csv_file
        self.limit = int(limit)

    def start_requests(self):
        try:
            with open(self.csv_file, 'r') as file:
                csv_reader = csv.reader(file)
                next(csv_reader, None)  # Skip header
                
                count = 0
                for row in csv_reader:
                    # Stop if we've reached the limit
                    if count >= self.limit:
                        self.logger.info(f"Reached limit of {self.limit} companies. Stopping.")
                        break
                    
                    EnterpriseNumber = row[0].strip()
                    EnterpriseNumberClean = EnterpriseNumber.replace('.', '')
                    
                    url = f"https://kbopub.economie.fgov.be/kbopub/toonondernemingps.html?ondernemingsnummer={EnterpriseNumberClean}&taal=fr"
                    headers = {
                        'Accept-Language': 'fr-FR,fr;q=0.9',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    self.logger.info(f"Processing company {count+1}/{self.limit}: {EnterpriseNumber}")
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse,
                        headers=headers,
                        meta={'EnterpriseNumber': EnterpriseNumber}
                    )
                    
                    count += 1
                    
        except FileNotFoundError:
            self.logger.error(f"CSV file not found: {self.csv_file}")
        except Exception as e:
            self.logger.error(f"Error reading CSV file: {e}")

    def parse(self, response):
        EnterpriseNumber = response.meta['EnterpriseNumber']

        # Vérification si on a bien atterri sur la bonne page
        if "captchaform" in response.url.lower():
            self.logger.warning(f"CAPTCHA triggered for {EnterpriseNumber}")
            return

        table_data = response.xpath('//div[@id="table"]/table//tr')
        data = []
        for row in table_data:
                cols = row.xpath('.//td')
                row_data = []
                for col in cols:
                    text = col.xpath('.//text()').get()
                    if text:
                        row_data.append(text.strip())
                if row_data:
                    data.append(row_data)
        
        relevant_data = self.extract_relevant_data(EnterpriseNumber, data)

        item = KboItem()
        item['EnterpriseNumber'] = relevant_data['EnterpriseNumber']
        item['Généralités'] = relevant_data['Généralités']
        item['Fonctions'] = relevant_data['Fonctions']
        item['Capacités_entrepreneuriales'] = relevant_data['Capacités entrepreneuriales']
        item['Qualités'] = relevant_data['Qualités']
        item['Autorisations'] = relevant_data['Autorisations']
        item['NACE_code'] = relevant_data['NACE code']
        item['Données_financières'] = relevant_data['Données financières']
        item['Liens_entre_entités'] = relevant_data['Liens entre entités']
        item['Liens_externes'] = relevant_data['Liens externes']

        yield item

    def extract_relevant_data(self, EnterpriseNumber, table_data):
        relevant_data = {
            'EnterpriseNumber': EnterpriseNumber,
            'Généralités': {},
            'Fonctions': [],
            'Capacités entrepreneuriales': '',
            'Qualités': [],
            'Autorisations': '',
            'NACE code': {
                '2025': '',
                '2008': '',
                '2003': ''
            },
            'Données financières': {},
            'Liens entre entités': [],
            'Liens externes': []
        }

        section = None
        for row in table_data:
            if len(row) == 1 and row[0] in ['Algemeen', 'Généralités', 'Functies', 'Ondernemersvaardigheden - ambulant - kermisuitbater', 'Hoedanigheden', 'Toelatingen', 'Financiële gegevens', 'Linken tussen entiteiten', 'Externe links', 'Activiteiten']:
                section = row[0]
                if section == 'Algemeen' or section == 'Généralités':
                    section = 'Généralités'
                elif section == 'Ondernemersvaardigheden - ambulant - kermisuitbater':
                    section = 'Capacités entrepreneuriales'
                elif section == 'Hoedanigheden':
                    section = 'Qualités'
                elif section == 'Toelatingen':
                    section = 'Autorisations'
                elif section == 'Financiële gegevens':
                    section = 'Données financières'
                elif section == 'Linken tussen entiteiten':
                    section = 'Liens entre entités'
                elif section == 'Externe links':
                    section = 'Liens externes'
                elif section == 'Activiteiten':
                    section = 'NACE code'
            elif section == 'Généralités':
                if len(row) == 2:
                    relevant_data['Généralités'][row[0].strip(':')] = row[1]
            elif section == 'Functies':
                if len(row) > 0:
                    relevant_data['Fonctions'].append(row[0])
            elif section == 'Capacités entrepreneuriales':
                relevant_data['Capacités entrepreneuriales'] = row[0] if row else ''
            elif section == 'Qualités':
                if len(row) > 0:
                    relevant_data['Qualités'].append(row[0])
            elif section == 'Autorisations':
                relevant_data['Autorisations'] = row[0] if row else ''
            elif section == 'NACE code':
                if 'Nacebelcode versie 2025' in row[0]:
                    relevant_data['NACE code']['2025'] = row[1] if len(row) > 1 else ''
                elif 'Nacebelcode versie 2008' in row[0]:
                    relevant_data['NACE code']['2008'] = row[1] if len(row) > 1 else ''
                elif 'Nacebelcode versie 2003' in row[0]:
                    relevant_data['NACE code']['2003'] = row[1] if len(row) > 1 else ''
            elif section == 'Données financières':
                if len(row) == 2:
                    relevant_data['Données financières'][row[0].strip(':')] = row[1]
            elif section == 'Liens entre entités':
                if len(row) > 0:
                    relevant_data['Liens entre entités'].append(row[0])
            elif section == 'Liens externes':
                if len(row) > 0:
                    relevant_data['Liens externes'].append(row[0])

        return relevant_data
