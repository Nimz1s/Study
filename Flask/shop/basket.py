from flask import Blueprint, render_template, session, redirect, url_for, flash, jsonify, request
from models import get_conect_bd
from datetime import datetime

basket_bp = Blueprint('basket_bp', __name__)

@basket_bp.route('/basket')
def view_basket():
    user_id = session.get('user_id')
    if not user_id:
        flash('Будь ласка, увійдіть в акаунт, щоб переглянути кошик')
        return redirect(url_for('login_bp.login'))

    conn = get_conect_bd()
    basket_items = conn.execute('''
        SELECT products.id, products.name_product, products.price, products.main_img, basket.quantity
        FROM products
        JOIN basket ON products.id = basket.product_id
        WHERE basket.user_id = ? AND basket.orders_id IS NULL
    ''', (user_id,)).fetchall()
    conn.close()

    if not basket_items:
        flash('Ваш кошик порожній')
    
    return render_template('basket.html', basket_items=basket_items)


@basket_bp.route('/update_quantity/<int:item_id>', methods=['POST'])
def update_quantity(item_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Будь ласка, увійдіть в акаунт'}), 400

    data = request.get_json()
    new_quantity = data.get('quantity')

    if not new_quantity or new_quantity <= 0:
        return jsonify({'error': 'Невірна кількість'}), 400

    conn = get_conect_bd()
    conn.execute('UPDATE basket SET quantity = ? WHERE user_id = ? AND product_id = ?', (new_quantity, user_id, item_id))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Кількість успішно оновлено'}), 200


@basket_bp.route('/add_to_basket/<int:item_id>', methods=['POST'])
def add_to_basket(item_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('Будь ласка, увійдіть в акаунт, щоб додати товар в кошик')
        return redirect(url_for('login_bp.login'))

    conn = get_conect_bd()
    existing_item = conn.execute('SELECT * FROM basket WHERE user_id = ? AND product_id = ? AND orders_id IS NULL', (user_id, item_id)).fetchone()

    if existing_item:
        # Збільшуємо кількість товару, якщо вже є в кошику
        conn.execute('UPDATE basket SET quantity = quantity + 1 WHERE user_id = ? AND product_id = ?', (user_id, item_id))
    else:
        # Додаємо товар, якщо його немає в кошику
        conn.execute('INSERT INTO basket (user_id, product_id, quantity) VALUES (?, ?, ?)', (user_id, item_id, 1))

    conn.commit()
    conn.close()
    flash('Товар додано до кошика')
    return redirect(url_for('home.main'))


@basket_bp.route('/remove_from_basket/<int:item_id>', methods=['POST'])
def remove_from_basket(item_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('Будь ласка, увійдіть в акаунт, щоб видалити товари з кошика')
        return redirect(url_for('login_bp.login'))

    conn = get_conect_bd()
    conn.execute('DELETE FROM basket WHERE user_id = ? AND product_id = ?', (user_id, item_id))
    conn.commit()
    conn.close()
    flash('Товар видалено з кошика')
    return redirect(url_for('basket_bp.view_basket'))


@basket_bp.route('/checkout', methods=['POST'])
def checkout():
    user_id = session.get('user_id')
    if not user_id:
        flash('Будь ласка, увійдіть в акаунт, щоб оформити замовлення')
        return redirect(url_for('login_bp.login'))

    # Отримуємо дані форми
    main_choice = request.form.get('main_choice')
    sub_choice = request.form.get('sub_choice') if main_choice == 'our_shop' else request.form.get('sub1_choice')
    lastname = request.form.get('lastname')
    firstname = request.form.get('firstname')
    email = request.form.get('email')
    phone = request.form.get('phone')

    # Перевірка на обов'язкові поля
    if not main_choice or not sub_choice:
        flash('Будь ласка, виберіть всі опції')
        return redirect(url_for('basket_bp.view_basket'))

    # Підключення до бази даних
    conn = get_conect_bd()

    # Отримання товарів з кошика
    basket_items = conn.execute('SELECT product_id, quantity FROM basket WHERE user_id = ? AND orders_id IS NULL', (user_id,)).fetchall()

    # Перевірка на наявність товарів в кошику
    if not basket_items:
        flash('Ваш кошик порожній')
        return redirect(url_for('home.main'))

    # Створення нового замовлення в таблиці 'orders'
    conn.execute('''
        INSERT INTO orders (sub_choice, lastname, firstname, email, phone, data, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (sub_choice, lastname, firstname, email, phone, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'Новий'))

    # Отримуємо ID останнього замовлення
    last_order_id = conn.execute('SELECT id FROM orders ORDER BY id DESC LIMIT 1').fetchone()[0]

    if not last_order_id:
        flash('Не вдалося створити замовлення')
        conn.close()
        return redirect(url_for('basket_bp.view_basket'))

    # Оновлюємо кошик, додаючи 'orders_id' для кожного товару
    for item in basket_items:
        product_id = item[0]  # Отримуємо ID товару
        quantity = item[1]  # Отримуємо кількість товару
        conn.execute('''
            UPDATE basket
            SET orders_id = ?
            WHERE user_id = ? AND product_id = ?
        ''', (last_order_id, user_id, product_id))  # Додаємо 'orders_id' для кожного товару

    # Видалення товарів з кошика після оформлення замовлення
    conn.execute('DELETE FROM basket WHERE user_id = ? AND orders_id IS NULL', (user_id,))

    # Комітуємо зміни
    conn.commit()
    conn.close()

    flash('Ваше замовлення було успішно оформлено')
    return redirect(url_for('home.main'))
