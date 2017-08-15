class ProductModel:
    def __init__(self, product_id, weight=0, product_loc=list()):
        self.productId = product_id
        self.weight = weight
        self.productLoc = product_loc
        self.rackId = None

    def set_product_weight(self, weight):
        self.weight = weight

    def set_product_loc(self, product_loc=list()):
        self.productLoc = product_loc

    def set_product2rack(self, rack_id):
        self.rackId = rack_id

    def __str__(self):
        return "{\"productId\":\"" + str(self.productId) + "}"
