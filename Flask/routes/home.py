from flask import Blueprint, render_template, request, url_for, redirect
from models import get_products, get_order_details
from math import ceil

home_bp = Blueprint('home', __name__)

# Визначаємо кількість продуктів на сторінку
PRODUCTS_PER_PAGE = 24

@home_bp.route('/', methods=['POST', 'GET'])
def main():
    if request.method == 'POST':
        # Обробка POST-запиту
        file = request.files.get('file')
        if file:
            # Логіка для обробки файлу
            return redirect(url_for('home.main'))
        return "Файл не обрано."

    # Параметри пагінації
    page = request.args.get('page', 1, type=int)
    products = get_products()
    total_products = len(products)
    total_pages = ceil(total_products / PRODUCTS_PER_PAGE)

    # Відображення продуктів для поточної сторінки
    start = (page - 1) * PRODUCTS_PER_PAGE
    end = start + PRODUCTS_PER_PAGE
    paginated_products = products[start:end]

    return render_template(
        'home.html',
        products=paginated_products,
        page=page,
        total_pages=total_pages
    )

@home_bp.route('/item/<int:item_id>')
def item(item_id):
    item = get_order_details(item_id)
    return render_template('item.html', item=item)
