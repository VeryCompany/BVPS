
class HumanModel():

    def __init__(self, humanId, humanLoc, shoppingCart):
        self.humanId=humanId
        self.humanLoc= humanLoc
        self.shoppingCart=shoppingCart
        self.humanLocHistroy = None

    def setComeTime(self, time):
        self.intime=time

    def setHumanLoc(self, humanLoc):
        self.humanLoc=humanLoc
        if self.humanLocHistroy is None:
            self.humanLocHistroy = dict()
        self.humanLocHistroy[humanLoc[0]]=humanLoc

    def getHumanLoc(self, time):
        if self.humanLocHistroy is None: return None;
        return self.humanLocHistroy[time]

    def addProductToCart(self, product):
        self.shoppingCart.append(product)

    def removeProductFromCart(self, product):
        self.shoppingCart.remove(product)

    def __str__(self):
        return "Human[humanId=" + self.humanId + ", humanLoc=" + str(self.humanLoc) + ", ShoppingCart=" + str(self.shoppingCart) + "]"