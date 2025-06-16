import os
import json
import pandas as pd
from app import utils
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

class Product:
    def __init__(self, product_id, product_name, opinions_count=0, pros_count=0, cons_count=0, average_stars=0):
        self.product_id = product_id
        self.product_name = product_name
        self.opinions_count = opinions_count
        self.pros_count = pros_count
        self.cons_count = cons_count
        self.average_stars = average_stars

    @classmethod
    def from_dict(cls, data):
        return cls(
            product_id=data.get("product_id"),
            product_name=data.get("product_name"),
            opinions_count=data.get("opinions_count", 0),
            pros_count=data.get("pros_count", 0),
            cons_count=data.get("cons_count", 0),
            average_stars=data.get("average_stars", 0)
        )

class Opinion:
    def __init__(self, opinion_id, author, recommendation, stars, content, pros, cons, useful, unuseful, post_date, purchase_date):
        self.opinion_id = opinion_id
        self.author = author
        self.recommendation = recommendation
        self.stars = stars
        self.content = content
        self.pros = pros
        self.cons = cons
        self.useful = useful
        self.unuseful = unuseful
        self.post_date = post_date
        self.purchase_date = purchase_date

    @classmethod
    def from_dict(cls, data):
        return cls(
            opinion_id=data.get("opinion_id"),
            author=data.get("author"),
            recommendation=data.get("recommendation"),
            stars=data.get("stars"),
            content=data.get("content"),
            pros=data.get("pros"),
            cons=data.get("cons"),
            useful=data.get("useful"),
            unuseful=data.get("unuseful"),
            post_date=data.get("post_date"),
            purchase_date=data.get("purchase_date")
        )

class ProductManager:
    @staticmethod
    def all():
        products = []
        for filename in os.listdir("./app/data/products"):
            with open(f"./app/data/products/{filename}", encoding="utf-8") as jf:
                data = json.load(jf)
                products.append(Product.from_dict(data))
        return products

    @staticmethod
    def get(product_id):
        with open(f"./app/data/products/{product_id}.json", encoding="utf-8") as jf:
            return Product.from_dict(json.load(jf))

    @staticmethod
    def save_stats(product_id, product_name, opinions_df):
        stats = {
            'product_id': product_id,
            'product_name': product_name,
            "opinions_count": opinions_df.shape[0],
            "pros_count": int(opinions_df.pros.astype(bool).sum()),
            "cons_count": int(opinions_df.cons.astype(bool).sum()),
            "pros_cons_count": int(opinions_df.apply(lambda o: bool(o.pros) and bool(o.cons), axis=1).sum()),
            "average_stars": float(opinions_df.stars.mean()),
            "pros": opinions_df.pros.explode().dropna().value_counts().to_dict(),
            "cons": opinions_df.cons.explode().dropna().value_counts().to_dict(),
            "recommendations": opinions_df.recommendation.value_counts(dropna=False).reindex(['Nie polecam', 'Polecam', None], fill_value=0).to_dict(),
        }
        os.makedirs("./app/data/products", exist_ok=True)
        with open(f"./app/data/products/{product_id}.json", "w", encoding="utf-8") as jf:
            json.dump(stats, jf, indent=4, ensure_ascii=False)

    @staticmethod
    def get_stats(product_id):
        with open(f"./app/data/products/{product_id}.json", encoding="utf-8") as jf:
            return json.load(jf)

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
        import requests
        from config import headers
        from bs4 import BeautifulSoup

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

class ChartManager:
    @staticmethod
    def generate_charts(product_id):
        os.makedirs("./app/static/images/charts", exist_ok=True)
        stats = ProductManager.get_stats(product_id)
        # Pie chart
        recommendations = pd.Series(stats['recommendations'])
        recommendations.plot.pie(
            label="",
            title=f"Rozkład rekomendacji w opiniach o produkcie {product_id}",
            labels=["Nie polecam", "Polecam", "Nie mam zdania"],
            colors=["#C05757", "#548A33", "#575757"],
            textprops={'fontsize': 12, 'color': '#B3B3B3'},
            autopct="%1.1f%%"
        )
        plt.title(f"Rozkład rekomendacji w opiniach o produkcie {product_id}",
                  color='#B3B3B3', fontsize=14, pad=20)
        plt.gcf().patch.set_facecolor('#36312B')
        plt.savefig(f"./app/static/images/charts/{stats['product_id']}_pie.png")
        plt.close()
        # Bar chart
        df = OpinionManager.to_dataframe(product_id)
        stars = df["stars"].value_counts().sort_index()
        stars.plot.bar(
            title=f"Rozkład gwiazdek dla produktu {product_id}",
            color="#548A33",
        )
        plt.gcf().patch.set_facecolor('#36312B')
        plt.gca().set_facecolor('#36312B')
        plt.title(f"Rozkład gwiazdek dla produktu {product_id}",
                  color='#B3B3B3', fontsize=16, pad=20)
        plt.xlabel("Liczba gwiazdek", color='#B3B3B3')
        plt.ylabel("Liczba opinii", color='#B3B3B3')
        plt.xticks(color='#B3B3B3')
        plt.yticks(color='#B3B3B3')
        plt.grid(True, alpha=0.3, color='#B3B3B3', axis='y')
        plt.savefig(f"./app/static/images/charts/{product_id}_bar.png",
                    facecolor='#36312B',
                    bbox_inches='tight')
        plt.close()