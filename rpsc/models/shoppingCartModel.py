class ShoppingCartProductModel(dict):
    def __init__(self, count):
        dict.__init__(self)
        self.default = None
        self.count = count

    def get_cart(self, key):
        if key is None:
            return None, 0

        if self.get(key) is None:
            return None, 0

        return self.get(key)

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except Exception as cartKeyError:
            print("ERROR:", cartKeyError)
            return self.default

    def add_product(self, product):
        if product is None:
            return

        product_dict, count = self.get_cart(product.productId)
        if product_dict is None:
            count = 1
            self.count += 1
            dict.__setitem__(self, product.productId, ("\"productId\":\"" + product.productId + "\"", count))
        else:
            count += 1
            dict.__setitem__(self, product.productId, ("\"productId\":\"" + product.productId + "\"", count))
            self.count += 1

    def remove_product(self, product_id):

        product_dict, count = self.get_cart(product_id)
        if product_dict is not None:
            if count > 1:
                count -= 1
                dict.__setitem__(self, product_id, ("\"productId\":\"" + product_id + "\"", count))
                self.count -= 1
            elif count == 1:
                self.pop(product_id)
                self.count -= 1

    def __str__(self):
        return "[" + ",".join("{" + str(self[product][0]) + ",\"count\":%s}"
                              % str(self[product][1]) for product in self) + "]"
