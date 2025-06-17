import os
import json
from app.models.product import Product

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
