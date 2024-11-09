from flask import Blueprint, render_template, request, url_for, session
from models import get_products

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def main():
    products = get_products()
    return render_template('home.html', productS=products)


# @home_bp.route('/item/<int:item_id>')
# def item_details(item_id):
#     product = get_products(item_id)
#     return render_template('item.html', product=product)
