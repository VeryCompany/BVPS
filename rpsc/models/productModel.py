
class ProductModel():

    def __init__(self, productId, productName, weight=0, productLoc=[], price=0):
        self.productId = productId
        self.productName = productName
        self.weight = weight
        self.productLoc = productLoc
        self.rackId = None
        self.price=price

    def setProductWeight(self, weight):
        self.weight = weight

    def setProductLoc(self, productLoc=[]):
        self.productLoc = productLoc

    def setProduct2Rack(self, rackId):
        self.rackId = rackId

    def __str__(self):
        extStr = ''
        # if self.rackId is not None:
        #     extStr = ", \"rackId\" : " + self.rackId + ", \"weigth\":" + str(self.weight) + ", \"productLoc\":" + str(self.productLoc)
        return "\"product\":{\"productId\":\"" + str(self.productId) + "\", \"productName\":\"" + str(self.productName) + "\", \"price\":" + str(self.price) + extStr + "}"