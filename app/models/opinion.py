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
