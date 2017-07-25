
class RackModel():
    """The Rack Model"""

    def __init__(self, rackId, productList=list(), rackLoc=[]):
        self.rackId = rackId
        self.rackLoc = rackLoc
        self.productList = productList
        self.productSize = len(self.productList)

    def setRackLoc(self, rackLoc):
        self.rackLoc = rackLoc

    def addProductList(self, product):
        self.productList.append(product)
        # self.productList=products

    def getProductSize(self):
        return len(self.productList)

    def __str__(self):
        return "RackModel[rackId=" + str(self.rackId) + ", productList=[" + ",".join(str(product) for product in self.productList) + "],productSize=" + str(self.getProductSize()) + ", rackLoc=" + str(self.rackLoc) + "]"