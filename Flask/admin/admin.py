import os
from flask import render_template, request, redirect, url_for, Blueprint, current_app, flash, session
from werkzeug.utils import secure_filename
from models import get_conect_bd, get_order_details


admin_bp = Blueprint('admin_bp', __name__)


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'Flask/static/img'
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Головна сторінка з інформацією про замовлення, відгуки, продукти та користувачів
@admin_bp.route('/admin')
def get_info():
    if session.get('is_admin') is not True:  # Перевірка, чи є в сесії ключ is_admin
        flash('У вас немає прав адміна')
        return redirect(url_for('home.main'))
    conn = get_conect_bd()
    order = conn.execute('SELECT * FROM orders').fetchall()
    feedbacks = conn.execute('SELECT * FROM feedbacks').fetchall()
    products = conn.execute('SELECT * FROM products').fetchall()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return render_template('admin.html', order=order, feedbacks=feedbacks, products=products, users=users)


@admin_bp.route('/admin/order_details/<int:order_id>', methods=['POST'])
def order_details(order_id):
    if session.get('is_admin') is not True:  # Перевірка, чи є в сесії ключ is_admin
        flash('У вас немає прав адміна')
        return redirect(url_for('home.main'))
    conn = get_conect_bd()
    order = conn.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
    items = conn.execute('SELECT b.quantity, p.id, p.name_product, p.price FROM basket b JOIN products p ON b.product_id = p.id WHERE b.orders_id = ?', (order_id,)).fetchall()

    return render_template('order_details.html', order=order, items=items)


@admin_bp.route('/admin/update_order_status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    if session.get('is_admin') is not True:  # Перевірка, чи є в сесії ключ is_admin
        flash('У вас немає прав адміна')
        return redirect(url_for('home.main'))
    status = request.form['status']
    conn = get_conect_bd()
    conn.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_bp.get_info'))


@admin_bp.route('/admin/delete_order/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    if session.get('is_admin') is not True:  # Перевірка, чи є в сесії ключ is_admin
        flash('У вас немає прав адміна')
        return redirect(url_for('home.main'))
    conn = get_conect_bd()
    conn.execute('DELETE FROM basket WHERE orders_id = ?', (order_id,))
    conn.execute('DELETE FROM orders WHERE id = ?', (order_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_bp.get_info'))


# Видалити відгук
@admin_bp.route('/admin/delete_feedback/<int:id>', methods=['POST'])
def delete_feedback(id):
    if session.get('is_admin') is not True:  # Перевірка, чи є в сесії ключ is_admin
        flash('У вас немає прав адміна')
        return redirect(url_for('home.main'))
    conn = get_conect_bd()
    conn.execute('DELETE FROM feedbacks WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_bp.get_info'))


# Сторінка продукту
@admin_bp.route('/admin/product/<int:product_id>', methods=['GET', 'POST'])
def details(product_id):
    if session.get('is_admin') is not True:  # Перевірка, чи є в сесії ключ is_admin
        flash('У вас немає прав адміна')
        return redirect(url_for('home.main'))
    if request.method == 'POST':
        # Отримуємо файл
        file = request.files.get('file')

        if not file:
            flash('Файл не обрано!', 'error')
            return redirect(url_for('admin_bp.details', product_id=product_id))

        if file and allowed_file(file.filename):
            # Забезпечуємо безпечне ім'я
            filename = secure_filename(file.filename)
            # Отримуємо шлях до папки завантаження
            upload_folder = current_app.config['UPLOAD_FOLDER']
            file_path = os.path.join(upload_folder, filename)

            # Зберігаємо файл
            file.save(file_path)

            file_path_in_db = f'img/{filename}'

            # Оновлюємо базу даних
            conn = get_conect_bd()
            conn.execute('UPDATE products SET main_img = ? WHERE id = ?', (file_path_in_db, product_id))
            conn.commit()
            conn.close()

            flash('Файл успішно завантажено!', 'success')
            return redirect(url_for('admin_bp.details', product_id=product_id))
        else:
            flash('Неприпустимий формат файлу.', 'error')

    # Завантаження даних продукту
    product = get_order_details(product_id)
    return render_template('product.html', product=product)


@admin_bp.route('/admin/product/update/<int:product_id>', methods=['POST'])
def update_product(product_id):
    if session.get('is_admin') is not True:  # Перевірка, чи є в сесії ключ is_admin
        flash('У вас немає прав адміна')
        return redirect(url_for('home.main'))
    # Отримуємо дані з форми
    name_product = request.form.get('name_product')
    info_for_product = request.form.get('info_for_product')
    price = request.form.get('price')
    file = request.files.get('file')

    # Перевірка на завантаження файлу
    file_path_in_db = None
    if file and file.filename:
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        file_path_in_db = f'img/{filename}'  # Додаємо префікс 'img/'

    # Оновлюємо базу даних
    conn = get_conect_bd()
    if file_path_in_db:
        conn.execute("""
            UPDATE products
            SET name_product = ?, info_for_product = ?, price = ?, main_img = ?
            WHERE id = ?
        """, (name_product, info_for_product, price, file_path_in_db, product_id))
    else:
        conn.execute("""
            UPDATE products
            SET name_product = ?, info_for_product = ?, price = ?
            WHERE id = ?
        """, (name_product, info_for_product, price, product_id))
    conn.commit()
    conn.close()

    # Flash-повідомлення про успішне оновлення
    flash('Дані продукту успішно оновлено!')

    # Перенаправлення назад на сторінку продукту
    return redirect(url_for('admin_bp.get_info'))


@admin_bp.route('/admin/delete_product/<int:products_id>', methods=['POST'])
def delete_product(products_id):
    if session.get('is_admin') is not True:  # Перевірка, чи є в сесії ключ is_admin
        flash('У вас немає прав адміна')
        return redirect(url_for('home.main'))
    conn = get_conect_bd()
    conn.execute('DELETE FROM products WHERE id = ?', (products_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_bp.get_info'))


@admin_bp.route('/admin/product/add', methods=['POST'])
def add_product():
    if session.get('is_admin') is not True:  # Перевірка, чи є в сесії ключ is_admin
        flash('У вас немає прав адміна')
        return redirect(url_for('home.main'))
    if request.method == 'POST':
        name_product = request.form.get('name_product')
        info_for_product = request.form.get('info_for_product')
        price = request.form.get('price')
        main_img = request.form.get('main_img')


        main_img = request.files.get('main_img')

        file_path = None
        if main_img and main_img.filename:  # Перевіряємо, чи є файл
            filename = secure_filename(main_img.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            main_img.save(file_path)
            file_path = f'img/{filename}'  # Додаємо префікс 'img/'

        conn = get_conect_bd()
        conn.execute('INSERT INTO products (name_product, info_for_product, price, main_img) VALUES (?, ?, ?, ?)',(name_product, info_for_product, price, file_path))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_bp.get_info'))
    


@admin_bp.route('/admin/rights_user/<int:user_id>', methods=['POST'])
def rights_user(user_id):
    if session.get('is_admin') is not True:  # Перевірка, чи є в сесії ключ is_admin
        flash('У вас немає прав адміна')
        return redirect(url_for('home.main'))
    conn = get_conect_bd()
    user = conn.execute('SELECT is_admin FROM users WHERE id = ?', (user_id, )).fetchone()
    if user['is_admin']:
        status_user = 0
        user = conn.execute('UPDATE users SET is_admin = ? WHERE id = ?', (status_user, user_id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_bp.get_info'))
    else:
        status_user = 1
        user = conn.execute('UPDATE users SET is_admin = ? WHERE id = ?', (status_user, user_id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_bp.get_info'))
