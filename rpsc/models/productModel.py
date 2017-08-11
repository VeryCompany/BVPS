class ProductModel:
    def __init__(self, product_id, product_name, weight=0, product_loc=list(), price=0):
        self.productId = product_id
        self.productName = product_name
        self.weight = weight
        self.productLoc = product_loc
        self.rackId = None
        self.price = price

    def set_product_weight(self, weight):
        self.weight = weight

    def set_product_loc(self, product_loc=list()):
        self.productLoc = product_loc

    def set_product2rack(self, rack_id):
        self.rackId = rack_id

    def __str__(self):
        ext_str = ''
        return "\"product\":{\"productId\":\"" + str(self.productId) + "\", \"productName\":\"" + str(
            self.productName) + "\", \"price\":" + str(self.price) + ext_str + "}"
