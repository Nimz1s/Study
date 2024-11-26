from flask import Blueprint, jsonify, session, request, current_app, flash, redirect, url_for
import os
import sqlite3
from admin.admin import allowed_file
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from models import get_conect_bd, get_products, get_order_details


api_bp = Blueprint('api', __name__)

# models

@api_bp.route('/models/api/get_products', methods=['GET'])
def api_get_producs():
    if 'user_id' not in session:
        return jsonify({
            "status": "error",
            "message": "You must be logged in to access this resource."
        }), 401
    if session.get('is_admin') is not True:  # Перевірка, чи є користувач адміністратором
        return jsonify({
            "status": "error",
            "message": "You do not have admin rights."
        }), 403
    
        
    try:
        products = get_products()
        if products:
            return jsonify({
                "status": "success",
                "data": products
            }), 200
        else:
            return jsonify({
                "status": "success",
                "data": [],
                "message": "No products"
            }), 200   
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e) 
        }), 500
    
@api_bp.route('/models/api/get_order_details/<int:item_id>', methods=['GET'])
def api_get_order_details(item_id):
    if 'user_id' not in session:
        return jsonify({
            "status": "error",
            "message": "You must be logged in to access this resource."
        }), 401
    if session.get('is_admin') is not True:  # Перевірка, чи є користувач адміністратором
        return jsonify({
            "status": "error",
            "message": "You do not have admin rights."
        }), 403
    try:
        item = get_order_details(item_id)
        if item:
            return jsonify({
                "status": "success",
                "data": dict(item)
            }), 200
        else:
            return jsonify({
            "status": "error",
            "data": None,
            "message": f"Product with ID {item_id} not found"
        }), 404
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    


# admin
@api_bp.route('/admin/api/get_info', methods=['GET'])
def api_get_info():
    if 'user_id' not in session:
        return jsonify({
            "status": "error",
            "message": "You must be logged in to access this resource."
        }), 401
    if session.get('is_admin') is not True:  # Перевірка, чи є користувач адміністратором
        return jsonify({
            "status": "error",
            "message": "You do not have admin rights."
        }), 403
    
    try:
        conn = get_conect_bd()
        
        # Отримання даних із таблиць
        orders = conn.execute('SELECT * FROM orders').fetchall()
        feedbacks = conn.execute('SELECT * FROM feedbacks').fetchall()
        products = conn.execute('SELECT * FROM products').fetchall()
        users = conn.execute('SELECT * FROM users').fetchall()
        conn.close()
        
        # Перетворення даних у списки словників
        orders = [dict(order) for order in orders]
        feedbacks = [dict(feedback) for feedback in feedbacks]
        products = [dict(product) for product in products]
        users = [dict(user) for user in users]
        
        # Повернення JSON-відповіді
        return jsonify({
            "status": "success",
            "data": {
                "orders": orders,
                "feedbacks": feedbacks,
                "products": products,
                "users": users
            }
        }), 200
    except Exception as e:
        # Обробка винятків
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500 


@api_bp.route('/api/admin/order_details/<int:order_id>', methods=['GET'])
def api_order_details(order_id):
    """
    API endpoint to retrieve details of a specific order.
    """
    # Перевірка, чи є користувач у сесії
    if 'user_id' not in session:
        return jsonify({
            "status": "error",
            "message": "You must be logged in to access this resource."
        }), 401  # 401 - Unauthorized

    # Перевірка прав адміністратора
    if session.get('is_admin') is not True:
        return jsonify({
            "status": "error",
            "message": "You do not have admin rights."
        }), 403  # 403 - Forbidden

    try:
        # Отримання даних із бази
        conn = get_conect_bd()
        order = conn.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
        items = conn.execute(
            '''
            SELECT b.quantity, p.id AS product_id, p.name_product, p.price
            FROM basket b
            JOIN products p ON b.product_id = p.id
            WHERE b.orders_id = ?
            ''',
            (order_id,)
        ).fetchall()
        conn.close()

        # Якщо замовлення не знайдено
        if not order:
            return jsonify({
                "status": "error",
                "message": f"Order with ID {order_id} not found."
            }), 404  # 404 - Not Found

        # Перетворення отриманих даних у словники
        order = dict(order)
        items = [dict(item) for item in items]

        # Повернення даних у форматі JSON
        return jsonify({
            "status": "success",
            "data": {
                "order": order,
                "items": items
            }
        }), 200  # 200 - OK

    except Exception as e:
        # Обробка винятків
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@api_bp.route('/api/admin/update_order_status/<int:order_id>', methods=['POST'])
def api_update_order_status(order_id):
    """
    API для оновлення статусу замовлення.
    """
    # Перевірка, чи є користувач у сесії
    if 'user_id' not in session:
        return jsonify({
            "status": "error",
            "message": "You must be logged in to access this resource."
        }), 401  # 401 - Unauthorized

    # Перевірка прав адміністратора
    if session.get('is_admin') is not True:
        return jsonify({
            "status": "error",
            "message": "You do not have admin rights."
        }), 403  # 403 - Forbidden

    # Отримання нового статусу із запиту
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({
            "status": "error",
            "message": "Missing 'status' in the request body."
        }), 400  # 400 - Bad Request

    status = data['status']

    try:
        conn = get_conect_bd()

        # Перевірка існування замовлення
        order = conn.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
        if not order:
            conn.close()
            return jsonify({
                "status": "error",
                "message": f"Order with ID {order_id} not found."
            }), 404  # 404 - Not Found

        # Оновлення статусу замовлення
        conn.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
        conn.commit()
        conn.close()

        return jsonify({
            "status": "success",
            "message": f"Order ID {order_id} status updated successfully to '{status}'."
        }), 200  # 200 - OK

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500  # 500 - Internal Server Error


@api_bp.route('/api/admin/delete_order/<int:order_id>', methods=['DELETE'])
def api_delete_order(order_id):
    """
    API для видалення замовлення.
    """
    # Перевірка авторизації
    if 'user_id' not in session:
        return jsonify({
            "status": "error",
            "message": "You must be logged in to access this resource."
        }), 401  # Unauthorized

    # Перевірка прав адміністратора
    if session.get('is_admin') is not True:
        return jsonify({
            "status": "error",
            "message": "You do not have admin rights."
        }), 403  # Forbidden

    try:
        conn = get_conect_bd()

        # Перевірка існування замовлення
        order = conn.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
        if not order:
            conn.close()
            return jsonify({
                "status": "error",
                "message": f"Order with ID {order_id} not found."
            }), 404  # Not Found

        # Видалення даних із бази
        conn.execute('DELETE FROM basket WHERE orders_id = ?', (order_id,))
        conn.execute('DELETE FROM orders WHERE id = ?', (order_id,))
        conn.commit()
        conn.close()

        return jsonify({
            "status": "success",
            "message": f"Order ID {order_id} and related basket items deleted successfully."
        }), 200  # OK

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500  # Internal Server Error


@api_bp.route('/api/admin/product/<int:product_id>', methods=['POST'])
def api_update_product_image(product_id):
    """
    API для оновлення зображення продукту.
    """
    # Перевірка авторизації
    if 'user_id' not in session:
        return jsonify({
            "status": "error",
            "message": "You must be logged in to access this resource."
        }), 401  # Unauthorized

    # Перевірка прав адміністратора
    if session.get('is_admin') is not True:
        return jsonify({
            "status": "error",
            "message": "You do not have admin rights."
        }), 403  # Forbidden

    # Перевірка наявності файлу у запиті
    file = request.files.get('file')
    if not file:
        return jsonify({
            "status": "error",
            "message": "No file provided in the request."
        }), 400  # Bad Request

    # Перевірка формату файлу
    if not allowed_file(file.filename):
        return jsonify({
            "status": "error",
            "message": "Invalid file format. Allowed formats are: png, jpg, jpeg, gif."
        }), 400  # Bad Request

    try:
        # Безпечне ім'я файлу
        filename = secure_filename(file.filename)

        # Отримуємо шлях до папки для збереження
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
        file_path = os.path.join(upload_folder, filename)

        # Зберігаємо файл
        file.save(file_path)

        # Формуємо шлях для збереження в базі
        file_path_in_db = f'img/{filename}'

        # Оновлюємо базу даних
        conn = get_conect_bd()
        conn.execute('UPDATE products SET main_img = ? WHERE id = ?', (file_path_in_db, product_id))
        conn.commit()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Product image updated successfully.",
            "data": {
                "product_id": product_id,
                "main_img": file_path_in_db
            }
        }), 200  # OK

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500  # Internal Server Error


from flask import jsonify

@api_bp.route('/api/admin/delete_product/<int:product_id>', methods=['DELETE'])
def api_delete_product(product_id):
    """API для видалення продукту за ID."""
    if not session.get('is_admin'):
        return jsonify({
            "status": "error",
            "message": "У вас немає прав адміністратора"
        }), 403  # Код 403: Заборонено

    try:
        conn = get_conect_bd()
        
        # Перевіряємо, чи існує продукт
        product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        if not product:
            return jsonify({
                "status": "error",
                "message": f"Продукт з ID {product_id} не знайдено"
            }), 404  # Код 404: Не знайдено

        # Видаляємо продукт
        conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
        conn.commit()
        conn.close()

        return jsonify({
            "status": "success",
            "message": f"Продукт з ID {product_id} успішно видалено"
        }), 200  # Код 200: Успішно

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Виникла помилка: {str(e)}"
        }), 500  # Код 500: Внутрішня помилка сервера


@api_bp.route('/admin/rights_user/<int:user_id>', methods=['POST'])
def rights_user(user_id):
    # Перевірка, чи є в сесії ключ is_admin
    if session.get('is_admin') is not True:
        flash('У вас немає прав адміна')
        return redirect(url_for('home.main'))

    try:
        # Підключення до бази даних
        conn = get_conect_bd()

        # Перевірка на існування користувача
        user = conn.execute('SELECT is_admin FROM users WHERE id = ?', (user_id,)).fetchone()
        
        # Якщо користувач не знайдений
        if not user:
            flash('Користувач не знайдений!')
            return redirect(url_for('admin_bp.get_info'))

        # Оновлення статусу прав користувача
        new_status = 0 if user['is_admin'] else 1
        conn.execute('UPDATE users SET is_admin = ? WHERE id = ?', (new_status, user_id))
        conn.commit()
        
        # Закриваємо підключення
        conn.close()

        # Показуємо успішне повідомлення
        flash('Права користувача успішно оновлено.')
        return redirect(url_for('admin_bp.get_info'))
    except Exception as e:
        # Обробка помилки
        flash(f'Виникла помилка: {str(e)}')
        return redirect(url_for('admin_bp.get_info'))


# accaunt
@api_bp.route('/accaunt', methods=['GET'])
def accaunt():
    if 'user_id' not in session:
        return jsonify({
            "status": "error",
            "message": "Ви не увійшли в акаунт."
        }), 401  # Повертаємо код 401, якщо користувач не авторизований

    user_id = session['user_id']

    try:
        # Отримуємо дані користувача за user_id
        conn = get_conect_bd()
        user = conn.execute('SELECT id, email, name, is_admin FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()

        if user:
            return jsonify({
                "status": "success",
                "data": user
            }), 200  # Повертаємо статус 200, якщо користувача знайдено
        else:
            return jsonify({
                "status": "error",
                "message": "Користувача не знайдено."
            }), 404  # Повертаємо статус 404, якщо користувача не знайдено

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Сталася помилка при отриманні інформації про користувача: {str(e)}"
        }), 500
    


# login
@api_bp.route('/login', methods=['POST'])
def login_api():
    # Отримуємо дані з POST-запиту
    email = request.json.get('email')
    password = request.json.get('password')

    if not email or not password:
        return jsonify({
            "status": "error",
            "message": "Email та пароль обов'язкові."
        }), 400  # Повертаємо код 400, якщо не надано email чи пароль

    try:
        # Підключення до бази даних
        conn = get_conect_bd()
        cursor = conn.cursor()

        # Отримання інформації про користувача за email
        user = cursor.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if user and check_password_hash(user['password'], password):  # Перевірка пароля
            session['user_id'] = user['id']
            session['email'] = user['email']
            is_admin = bool(user['is_admin'])  # Перевірка статусу адміністратора

            # Встановлення додаткових прав для адміністратора
            if is_admin:
                session['is_admin'] = True
                return jsonify({
                    "status": "success",
                    "message": "Ви увійшли як адміністратор",
                    "is_admin": True
                }), 200
            else:
                session['is_admin'] = False
                return jsonify({
                    "status": "success",
                    "message": "Ви увійшли як звичайний користувач",
                    "is_admin": False
                }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Логін або пароль невірний"
            }), 401  # Повертаємо код 401, якщо пароль чи email невірні

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Сталася помилка при вході: {str(e)}"
        }), 500  # Повертаємо код 500 в разі помилки сервера
    finally:
        conn.close()


@api_bp.route('/logout', methods=['POST'])
def logout_api():
    try:
        # Видаляємо дані користувача з сесії
        session.pop('user_id', None)
        session.pop('userinfo', None)
        session.pop('email', None)
        session.pop('is_admin', None)

        return jsonify({
            "status": "success",
            "message": "Ви вийшли з акаунта."
        }), 200  # Повертаємо успішну відповідь зі статусом 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Сталася помилка: {str(e)}"
        }), 500


@api_bp.route('/registration', methods=['POST'])
def registration_api():
    # Отримуємо дані з JSON-запиту
    data = request.get_json()

    # Перевіряємо, чи всі необхідні поля надані
    if not data or not all(k in data for k in ("userinfo", "phone", "email", "password")):
        return jsonify({
            "status": "error",
            "message": "Будь ласка, надайте всі необхідні дані (userinfo, phone, email, password)."
        }), 400  # Повертаємо код 400, якщо деякі поля відсутні

    userinfo = data['userinfo']
    phonenumber = data['phone']
    email = data['email']
    password = data['password']

    # Генерація хешу паролю
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    # Підключення до бази даних
    conn = get_conect_bd()

    try:
        # Перевірка, чи є вже користувач з таким email
        existing_user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        if existing_user:
            return jsonify({
                "status": "error",
                "message": "Користувач з таким email вже існує."
            }), 400  # Повертаємо помилку, якщо email вже зареєстрований

        # Вставка нового користувача в базу даних
        conn.execute('INSERT INTO users(userinfo, email, phonenumber, password, is_admin) VALUES (?, ?, ?, ?, ?)', 
                     (userinfo, email, phonenumber, hashed_password, 0))
        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Реєстрація успішна!"
        }), 201  # Повертаємо код 201, що означає, що ресурс створено

    except sqlite3.IntegrityError:
        return jsonify({
            "status": "error",
            "message": "Сталася помилка при реєстрації. Спробуйте пізніше."
        }), 500  # Повертаємо код 500 в разі помилки бази даних

    finally:
        conn.close()



# like
@api_bp.route('/add/<int:item_id>', methods=['POST'])
def add_to_like_api(item_id):
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({
            "status": "error",
            "message": "Будь ласка, увійдіть в акаунт, щоб додати в обране"
        }), 401  # Відповідь 401: Неавторизований доступ
    
    try:
        conn = get_conect_bd()
        
        # Перевіряємо, чи товар вже є в обраному
        existing_item = conn.execute('SELECT * FROM likes WHERE user_id = ? AND item_id = ?', (user_id, item_id)).fetchone()
        
        if not existing_item:
            # Якщо товар не в обраному, додаємо його
            conn.execute('INSERT INTO likes(user_id, item_id) VALUES (?, ?)', (user_id, item_id))
            conn.commit()
            return jsonify({
                "status": "success",
                "message": "Товар додано до обраного"
            }), 201  # Відповідь 201: Створено
        
        else:
            return jsonify({
                "status": "info",
                "message": "Товар вже є в обраному"
            }), 200  # Відповідь 200: Все добре, але товар вже в обраному
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Сталася помилка: {str(e)}"
        }), 500  # Відповідь 500: Помилка на сервері
    
    finally:
        conn.close()


@api_bp.route('/like', methods=['GET'])
def show_likes_api():
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({
            "status": "error",
            "message": "Будь ласка, увійдіть в акаунт, щоб переглянути обране"
        }), 401  # Відповідь 401: Неавторизований доступ
    
    try:
        conn = get_conect_bd()
        
        # Отримуємо обрані товари для поточного користувача
        items = conn.execute(''' 
            SELECT products.id, products.name_product, products.price, products.main_img
            FROM products
            JOIN likes ON products.id = likes.item_id
            WHERE likes.user_id = ?
        ''', (user_id,)).fetchall()
        
        conn.close()
        
        if items:
            # Якщо є товари в обраному, повертаємо їх
            return jsonify({
                "status": "success",
                "data": items
            }), 200  # Відповідь 200: Все добре, товари знайдені
        
        else:
            return jsonify({
                "status": "info",
                "message": "У вас немає обраних товарів"
            }), 200  # Відповідь 200: Все добре, але немає обраних товарів
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Сталася помилка: {str(e)}"
        }), 500
    

@api_bp.route('/remove_from_like/<int:item_id>', methods=['POST'])
def remove_from_like_api(item_id):
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({
            "status": "error",
            "message": "Будь ласка, увійдіть в акаунт, щоб видалити товари з обраного"
        }), 401  # Відповідь 401: Неавторизований доступ
    
    try:
        conn = get_conect_bd()
        
        # Видалення товару з обраного
        conn.execute('DELETE FROM likes WHERE user_id = ? AND item_id = ?', (user_id, item_id))
        conn.commit()
        conn.close()
        
        return jsonify({
            "status": "success",
            "message": "Товар видалено з обраного"
        }), 200  # Відповідь 200: Успішно видалено
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Сталася помилка: {str(e)}"
        }), 500
    


# basket
@api_bp.route('/remove_from_basket/<int:item_id>', methods=['POST'])
def remove_from_basket_api(item_id):
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({
            "status": "error",
            "message": "Будь ласка, увійдіть в акаунт, щоб видалити товари з кошика"
        }), 401  # Відповідь 401: Неавторизований доступ
    
    try:
        conn = get_conect_bd()
        
        # Видалення товару з кошика
        conn.execute('DELETE FROM basket WHERE user_id = ? AND product_id = ?', (user_id, item_id))
        conn.commit()
        conn.close()
        
        return jsonify({
            "status": "success",
            "message": "Товар видалено з кошика"
        }), 200  # Відповідь 200: Успішно видалено
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Сталася помилка: {str(e)}"
        }), 500
    

@api_bp.route('/add_to_basket/<int:item_id>', methods=['POST'])
def add_to_basket_api(item_id):
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({
            "status": "error",
            "message": "Будь ласка, увійдіть в акаунт, щоб додати товар в кошик"
        }), 401  # Відповідь 401: Неавторизований доступ
    
    try:
        conn = get_conect_bd()

        # Перевірка, чи товар вже є в кошику
        existing_item = conn.execute('SELECT * FROM basket WHERE user_id = ? AND product_id = ? AND orders_id IS NULL', (user_id, item_id)).fetchone()
        
        if existing_item:
            # Збільшуємо кількість товару, якщо він вже є в кошику
            conn.execute('UPDATE basket SET quantity = quantity + 1 WHERE user_id = ? AND product_id = ?', (user_id, item_id))
        else:
            # Додаємо товар в кошик
            conn.execute('INSERT INTO basket (user_id, product_id, quantity) VALUES (?, ?, ?)', (user_id, item_id, 1))

        conn.commit()
        conn.close()
        
        return jsonify({
            "status": "success",
            "message": "Товар додано до кошика"
        }), 200  # Відповідь 200: Успішно додано в кошик
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Сталася помилка: {str(e)}"
        }), 500
    

@api_bp.route('/basket', methods=['GET'])
def view_basket_api():
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({
            "status": "error",
            "message": "Будь ласка, увійдіть в акаунт, щоб переглянути кошик"
        }), 401  # Відповідь 401: Неавторизований доступ

    try:
        conn = get_conect_bd()

        # Отримуємо товари з кошика для поточного користувача
        basket_items = conn.execute('''
            SELECT products.id, products.name_product, products.price, products.main_img, basket.quantity
            FROM products
            JOIN basket ON products.id = basket.product_id
            WHERE basket.user_id = ? AND basket.orders_id IS NULL
        ''', (user_id,)).fetchall()

        conn.close()

        if not basket_items:
            return jsonify({
                "status": "success",
                "message": "Ваш кошик порожній",
                "data": []
            }), 200  # Повертаємо порожній кошик як успішну відповідь

        # Повертаємо товари з кошика
        return jsonify({
            "status": "success",
            "message": "Товари в кошику",
            "data": [{
                "product_id": item[0],
                "name_product": item[1],
                "price": item[2],
                "main_img": item[3],
                "quantity": item[4]
            } for item in basket_items]
        }), 200  # Відповідь з товаром у кошику
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Сталася помилка: {str(e)}"
        }), 500