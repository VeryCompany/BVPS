class ShoppingCartProductModel(dict):

    def __init__(self, count):
        dict.__init__(self)
        self.default = None
        self.count = count

    def getCart(self, key):
        if key is None: return None,0;

        if self.get(key) is None: return None,0;
        return self.get(key)

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except Exception as KeyError:
            return self.default

    def addProduct(self, product):
        if product is None: return ;

        productDict,count = self.getCart(product.productId)
        if productDict is None:
            productDict = product
            count = 1
            self.count += 1
            dict.__setitem__(self, productDict.productId, (productDict, count))
        else:
            count += 1
            dict.__setitem__(self, productDict.productId, (productDict, count))
            self.count += 1
        print count

    def removeProduct(self, productId):

        productDict, count = self.getCart(productId)
        if productDict is not None:
            if count > 1:
                count -= 1
                dict.__setitem__(self, productDict.productId, (productDict, count))
                self.count -= 1
            elif count == 1:
                self.pop(productId)
                self.count -= 1

    # def __str__(self):
    #     return "ShoppingCartProduct[" + ",".join("{" + str(self[product][0])+",count=%s}"%str(self[product][1]) for product in self) +"], ShoppingCartCount=" + str(self.count)

    def __str__(self):
        return "[" + ",".join("{" + str(self[product][0])+",\"count\":%s}"%str(self[product][1]) for product in self) + "]"