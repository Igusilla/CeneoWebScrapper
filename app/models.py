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