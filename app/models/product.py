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

