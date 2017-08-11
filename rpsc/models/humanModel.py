class HumanModel:
    def __init__(self, human_id, human_loc, shopping_cart):
        self.humanId = human_id
        self.humanLoc = human_loc
        self.shoppingCart = shopping_cart
        self.humanLocHistory = None
        self.inTime = None

    def set_come_time(self, time):
        self.inTime = time

    def set_human_loc(self, human_loc):
        self.humanLoc = human_loc
        if self.humanLocHistory is None:
            self.humanLocHistory = dict()
        self.humanLocHistory[human_loc[0]] = human_loc

    def get_human_loc(self, time):
        if self.humanLocHistory is None:
            return None
        return self.humanLocHistory[time]

    def add_product_to_cart(self, product):
        self.shoppingCart.append(product)

    def remove_product_from_cart(self, product):
        self.shoppingCart.remove(product)

    def __str__(self):
        return "Human[humanId=" + self.humanId + ", humanLoc=" + str(self.humanLoc) + ", ShoppingCart=" + str(
            self.shoppingCart) + "]"
