# -*- coding: utf-8 -*-

rackList=[
    {"id":"1","loc":[50, 50]},
    {"id":"2","loc":[150, 50]}
]

# productList=[
#     {"productId": "1_1", "productName": "产品1_1", "loc": [1, 1], "rackId": "1", "price":  50},
#     {"productId": "1_1", "productName": "产品1_1", "loc": [1, 2], "rackId": "1", "price":  50},
#     {"productId": "1_1", "productName": "产品1_1", "loc": [1, 3], "rackId": "1", "price":  50},
#     {"productId": "1_2", "productName": "产品1_2", "loc": [1, 4], "rackId": "1", "price":  50},
#     {"productId": "1_2", "productName": "产品1_2", "loc": [1, 5], "rackId": "1", "price":  50},
#     {"productId": "1_6", "productName": "产品1_6", "loc": [1, 6], "rackId": "1", "price": 150},
#     {"productId": "1_7", "productName": "产品1_7", "loc": [1, 7], "rackId": "1", "price": 150},
#     {"productId": "1_8", "productName": "产品1_8", "loc": [1, 8], "rackId": "1", "price": 150},
#     {"productId": "2_1", "productName": "产品2_1", "weight": 100, "rackId": "2", "price":  30},
#     {"productId": "2_1", "productName": "产品2_1", "weight": 100, "rackId": "2", "price":  30},
#     {"productId": "2_1", "productName": "产品2_1", "weight": 100, "rackId": "2", "price":  30},
#     {"productId": "2_1", "productName": "产品2_1", "weight": 100, "rackId": "2", "price":  30},
#     {"productId": "2_1", "productName": "产品2_1", "weight": 100, "rackId": "2", "price":  30},
#     {"productId": "2_1", "productName": "产品2_1", "weight": 100, "rackId": "2", "price":  30},
#     {"productId": "2_2", "productName": "产品2_2", "weight": 200, "rackId": "2", "price":  60},
#     {"productId": "2_3", "productName": "产品2_3", "weight": 300, "rackId": "2", "price":  90},
#     {"productId": "2_4", "productName": "产品2_4", "weight": 400, "rackId": "2", "price": 120},
#     {"productId": "2_5", "productName": "产品2_5", "weight": 500, "rackId": "2", "price": 150},
#     {"productId": "2_6", "productName": "产品2_6", "weight": 600, "rackId": "2", "price": 180},
#     {"productId": "2_7", "productName": "产品2_7", "weight": 700, "rackId": "2", "price": 210},
#     {"productId": "2_8", "productName": "产品2_8", "weight": 800, "rackId": "2", "price": 240}
# ]


"""
6921355232226: "烧酸奶", 6925303722562: "冰红茶", 6925303722432:"绿茶", 6903252014266:"方便面"
69025143: "益达-香浓蜜瓜味", 6923450690703: "绿箭薄荷糖-脆皮软心", 6923450603574: "彩虹糖原果味"
"""
productList=[
    {"productId": "6921355232226", "loc": [1, 1], "rackId": "1"},
    {"productId": "6921355232226", "loc": [1, 2], "rackId": "1"},
    {"productId": "6921355232226", "loc": [1, 3], "rackId": "1"},
    {"productId": "6925303722562", "loc": [1, 4], "rackId": "1"},
    {"productId": "6925303722562", "loc": [1, 5], "rackId": "1"},
    {"productId": "6925303722432", "loc": [1, 6], "rackId": "1"},
    {"productId": "1_7", "loc": [1, 7], "rackId": "1"},
    {"productId": "1_8", "loc": [1, 8], "rackId": "1"},
    {"productId": "6903252014266", "weight": 135, "rackId": "2"},
    {"productId": "6903252014266", "weight": 135, "rackId": "2"},
    {"productId": "6903252014266", "weight": 135, "rackId": "2"},
    {"productId": "6903252014266", "weight": 135, "rackId": "2"},
    {"productId": "6903252014266", "weight": 135, "rackId": "2"},
    {"productId": "6903252014266", "weight": 135, "rackId": "2"},
    {"productId": "6903252014266", "weight": 135, "rackId": "2"},
    {"productId": "6903252014266", "weight": 135, "rackId": "2"},
    {"productId": "6903252014266", "weight": 135, "rackId": "2"},
    {"productId": "6903252014266", "weight": 135, "rackId": "2"},
    {"productId": "6903252014266", "weight": 135, "rackId": "2"},
    {"productId": "6923450603574", "weight": 40, "rackId": "2"},
    {"productId": "6923450603574", "weight": 40, "rackId": "2"},
    {"productId": "6923450603574", "weight": 40, "rackId": "2"},
    {"productId": "6923450603574", "weight": 40, "rackId": "2"},
    {"productId": "69025143", "weight": 72, "rackId": "2"},
    {"productId": "69025143", "weight": 72, "rackId": "2"},
    {"productId": "69025143", "weight": 72, "rackId": "2"},
    {"productId": "69025143", "weight": 72, "rackId": "2"},
    {"productId": "6923450690703", "weight": 108, "rackId": "2"},
    {"productId": "6923450690703", "weight": 108, "rackId": "2"},
    {"productId": "6923450690703", "weight": 108, "rackId": "2"},
    {"productId": "6923450690703", "weight": 108, "rackId": "2"}
]

# 0x58EF, 0x5959

# beaconList = [
#     0x5A02, 0x5783, 0x5920, 0x58C3, 0x5967
# ]

beaconList = [
    0x5A02, 0x5783, 0x5920, 0x58C3, 0x5967, 0x5959, 0x58EF
]

regions = [{"id":"COMFAST", "uuid":"FDA50693-A4E2-4FB1-AFCF-C6EB07647825"}]

rack_loc = [
    {"rackId":"1", "beaconLoc":[1, 2, 5]},
    {"rackId":"2", "beaconLoc":[1, 2, 5]}
]