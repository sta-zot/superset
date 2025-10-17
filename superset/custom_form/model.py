"""
В этом модуле определяются модели для работы с базами данных для пользовательских форм.
"""


import json
import logging

import pandas as pd


class LocalesModel():

    def __init__(self, locale: str = "en"):
        self.locale = locale
        self.locales = self.__load_locales()

    def __load_locales(self):
        try:
            locales = pd.read_csv("https://raw.githubusercontent.com/sta-zot/SRW/refs/heads/main/data/locations.csv")
            
        except Exception as e:
            logging.error(f"Error loading locales: {e}")
            locales = pd.DataFrame({
                "region": ["Рязанская область", "Московская область","Ленинградская область"],
                "municipality": ["Рязанcский район", "Московский район","Ленинградский район"],
                "settlement": ["г. Рязань", "г. Москва","г. Санкт-Петербург"]
            })
        return locales

    def get_regions(self):
        return self.locales["region"].unique().tolist()
    
    def get_municipalities(self, region: str):
        return self.locales[self.locales["region"] == region]["municipality"].unique().tolist()
    
    def get_settlements(self, municipality: str):
        if municipality == "":
            return (self.locales["type"] + '. ' + self.locales["settlement"]).tolist()
        filtered_df = self.locales[self.locales["municipality"] == municipality]
        #print(filtered_df.count())
        return (filtered_df["type"] + '. ' + filtered_df["settlement"]).unique().tolist()
    
    def get_df(self)-> pd.DataFrame:
        return self.locales
    


if __name__ == "__main__":
    test_df  = LocalesModel()
    regions = test_df.get_regions()
    regions_index = [i for i in range(len(regions))]
    for region in regions:
        print(f"Region: {region}\t ID: {regions.index(region)}")  


