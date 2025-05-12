import scrapy
import csv

class EjusticeSpider(scrapy.Spider):
    name = "ejustice"

    def start_requests(self):
        with open('enterprise.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            for row in reader:
                if count >= 5:
                    break
                enterprise_number = row['EnterpriseNumber']
                url = f'https://www.ejustice.just.fgov.be/cgi_tsv/list.pl?btw={enterprise_number}'
                yield scrapy.Request(url, callback=self.parse)
                count += 1

    def parse(self, response):
    # Extract list items
        list_items = response.xpath('//div[@class="list-item"]')

        # Create a dictionary to store the publication data
        publications = []
        for item in list_items:
            text = item.xpath('.//text()').getall()
            text = ''.join([t.strip() for t in text]).strip()

            # Extract fields
            numero_publication = None
            titre_publication = None
            adresse_publication = None
            type_publication = None
            date_publication = None
            reference_publication = None
            url_image = None

            lines = text.split('\n')
            for i, line in enumerate(lines):
                if line.startswith(str(i+1) + ')'):
                    numero_publication = i+1
                    titre_publication = line.strip().replace(str(i+1) + ')', '').strip()
                if 'GERAARDSBERGEN' in line:
                    adresse_publication = 'GERAARDSBERGEN'
                if 'FIN DE SECTION' in line or 'CESSATION' in line or 'NULLITE' in line:
                    type_publication = 'Fin de section'
                if '/' in line and len(line.strip().split('/')) == 2:
                    date_publication = line.strip().split('/')[0].strip()
                    reference_publication = line.strip()

            links = item.xpath('.//a')
            for link in links:
                href = link.xpath('@href').get()
                if href and href.endswith('.pdf'):
                    url_image = response.urljoin(href)

            publication = {
                'Numéro de publication': numero_publication,
                'Titre de la publication + Code': titre_publication,
                'Adresse de publication': adresse_publication,
                'Type de publication': type_publication,
                'Date de publication': date_publication,
                'Référence de publication': reference_publication,
                'URL de l\'image': url_image,
            }
            publications.append(publication)

        # Yield the publication data
        yield {
            'enterprise_number': response.url.split('=')[-1],
            'publications': publications,
        }
