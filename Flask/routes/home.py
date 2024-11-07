from flask import Blueprint, render_template, request, url_for, session
from models import get_products

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def main():
    products = get_products()
    return render_template('home.html', products=products)