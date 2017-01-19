from webstore.models import db, Product
from flask import session

from datetime import datetime

## This class represents the cart of an user.
class Cart(object):
    def __init__(self, cart):
        self.items = cart

    def addToCart(self, productId, price):
        self.items[str(productId)] = {
            "price": price,
            "quantity": 1
        }

    def is_empty(self):
        return not bool(self.items)

    def deleteFromCart(self, productId):
        del self.items[str(productId)]

    def updateQuantity(self, productId, newQuantity):
        self.items[str(productId)]["quantity"] = newQuantity

    def getTotal(self):
        total = 0
        for item in self.items:
            total += self.items[item]["quantity"] * self.items[item]["price"]
        return total

    def getProductData(self):
        data = []
        for product_id in self.items:
            data.append(Product.query.filter_by(id=product_id).first())
        return data

    def get_products_ids(self):
        return self.items.keys()

    def get_quantity_by_id(self, product_id):
        return self.items[str(product_id)]["quantity"]
