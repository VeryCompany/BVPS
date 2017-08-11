class RackModel:
    """The Rack Model"""

    def __init__(self, rack_id, product_list=list(), rack_loc=list()):
        self.rackId = rack_id
        self.rackLoc = rack_loc
        self.productList = product_list
        self.productSize = len(self.productList)

    def set_rack_loc(self, rack_loc):
        self.rackLoc = rack_loc

    def add_product_list(self, product):
        self.productList.append(product)
        # self.productList=products

    def get_product_size(self):
        return len(self.productList)

    def __str__(self):
        return "RackModel[rackId=" + str(self.rackId) + ", " \
                                                        "productList=[" + ",".join(
            str(product) for product in self.productList) + "]," \
                                                            "productSize=" + str(
            self.get_product_size()) + ", rackLoc=" + str(self.rackLoc) + "]"
