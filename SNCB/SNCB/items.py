import scrapy

class KboItem(scrapy.Item):
    EnterpriseNumber = scrapy.Field()
    Généralités = scrapy.Field()
    Fonctions = scrapy.Field()
    Capacités_entrepreneuriales = scrapy.Field()
    Qualités = scrapy.Field()
    Autorisations = scrapy.Field()
    NACE_code = scrapy.Field()
    Données_financières = scrapy.Field()
    Liens_entre_entités = scrapy.Field()
    Liens_externes = scrapy.Field()
