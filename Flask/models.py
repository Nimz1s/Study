import sqlite3


def get_conect_bd():
    conn = sqlite3.connect('Flask/my_database.sqlite')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with sqlite3.connect('Flask/my_database.sqlite') as db:
        db = get_conect_bd()
        db.execute('CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT, name_product TEXT, info_for_product TEXT, price REAL, main_img TEXT, dop_img1 TEXT, dop_img2 TEXT)')
        db.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, userinfo TEXT NOT NULL UNIQUE, email TEXT NOT NULL UNIQUE, phonenumber INTEGER NOT NULL, password TEXT NOT NULL, is_admin INTEGER)')
        db.execute('CREATE TABLE IF NOT EXISTS basket(id INTEGER PRIMARY KEY AUTOINCREMENT, orders_id, user_id INTEGER NOT NULL, product_id INTEGER, quantity INTEGER, FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (product_id) REFERENCES products(id))')
        db.execute('CREATE TABLE IF NOT EXISTS likes(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, item_id INTEGER)')
        db.execute('CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT, sub_choice TEXT, lastname TEXT, firstname TEXT, email TEXT, phone INTEGER, data, status TEXT)')
        db.execute('CREATE TABLE IF NOT EXISTS feedbacks(id INTEGER PRIMARY KEY AUTOINCREMENT, user_info TEXT, email TEXT, data, message TEXT)')
        db.commit()
        db.close()


with sqlite3.connect('Flask/my_database.sqlite') as db:
    pass  #створює базу (вперше)
    conn = db.cursor()
    conn.execute('CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT, name_product TEXT, info_for_product TEXT, price REAL, main_img TEXT, dop_img1 TEXT, dop_img2 TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, userinfo TEXT NOT NULL UNIQUE, email TEXT NOT NULL UNIQUE, phonenumber INTEGER NOT NULL, password TEXT NOT NULL, is_admin INTEGER)')
    conn.execute('CREATE TABLE IF NOT EXISTS basket(id INTEGER PRIMARY KEY AUTOINCREMENT, orders_id, user_id INTEGER NOT NULL, product_id INTEGER, quantity INTEGER, FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (product_id) REFERENCES products(id))')
    conn.execute('CREATE TABLE IF NOT EXISTS likes(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, item_id INTEGER)') 
    conn.execute('CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT, sub_choice TEXT, lastname TEXT, firstname TEXT, email TEXT, phone INTEGER, data, status TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS feedbacks(id INTEGER PRIMARY KEY AUTOINCREMENT, user_info TEXT, email TEXT, data, message TEXT)')

   
def get_products():
    conn = get_conect_bd()
    products = conn.execute('SELECT id, name_product, main_img FROM products').fetchall()
    conn.close()
    return [dict(row) for row in products]



def get_order_details(item_id):
    conn = get_conect_bd()
    item = conn.execute('SELECT * FROM products WHERE id = ?', (item_id,)).fetchone()
    conn.close()
    return item


# def get_user_info(user_id):
#     conn = get_conect_bd()
#     user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
#     conn.close()
#     return user