import os
import json
import pandas as pd
import requests
from app import utils
from app.models.opinion import Opinion
from app.managers.product_manager import ProductManager
from config import headers
from bs4 import BeautifulSoup

class OpinionManager:
    @staticmethod
    def all(product_id):
        with open(f"./app/data/opinions/{product_id}.json", encoding="utf-8") as jf:
            return [Opinion.from_dict(op) for op in json.load(jf)]

    @staticmethod
    def save_all(product_id, opinions):
        os.makedirs("./app/data/opinions", exist_ok=True)
        with open(f"./app/data/opinions/{product_id}.json", "w", encoding="utf-8") as jf:
            json.dump([op.__dict__ for op in opinions], jf, indent=4, ensure_ascii=False)

    @staticmethod
    def from_scraping(product_id):
        next_page = f"https://www.ceneo.pl/{product_id}#tab=reviews"
        response = requests.get(next_page, headers=headers)
        if response.status_code != 200:
            return None, "Nie znaleziono produktu o podanym id"
        page_dom = BeautifulSoup(response.text, "html.parser")
        product_name = utils.extract_feature(page_dom, "h1")
        opinions_count = utils.extract_feature(page_dom, "a.product-review__link > span")
        if not opinions_count:
            return None, "Dla produktu o podanym id nie ma jeszcze żadnych opinii"
        all_opinions = []
        while next_page:
            response = requests.get(next_page, headers=headers)
            if response.status_code == 200:
                page_dom = BeautifulSoup(response.text, "html.parser")
                opinions = page_dom.select("div.js_product-review:not(.user-post--highlight)")
                for opinion in opinions:
                    single_opinion = {
                        key: utils.extract_feature(opinion, *value)
                        for key, value in utils.selectors.items()
                    }
                    all_opinions.append(single_opinion)
                try:
                    next_page = "https://www.ceneo.pl" + utils.extract_feature(page_dom, "a.pagination__next", "href")
                except TypeError:
                    next_page = None
            else:
                next_page = None
        opinions_objs = [Opinion.from_dict(op) for op in all_opinions]
        OpinionManager.save_all(product_id, opinions_objs)
        opinions_df = pd.DataFrame.from_dict(all_opinions)
        opinions_df.stars = opinions_df.stars.apply(lambda s: s.split("/")[0].replace(",", ".")).astype(float)
        opinions_df.useful = opinions_df.useful.astype(int)
        opinions_df.unuseful = opinions_df.unuseful.astype(int)
        ProductManager.save_stats(product_id, product_name, opinions_df)
        return product_name, None

    @staticmethod
    def to_dataframe(product_id):
        opinions = OpinionManager.all(product_id)
        return pd.DataFrame([op.__dict__ for op in opinions])
