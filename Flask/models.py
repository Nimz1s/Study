import sqlite3


def get_conect_bd():
    conn = sqlite3.connect('Flask/my_database.sqlite')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conect_bd()
    conn.execute('CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT, name_product TEXT, price REAL, main_img TEXT, dop_img1 TEXT, dop_img2 TEXT)')
    conn.commit()
    conn.close()

# with sqlite3.connect('Flask/my_database.sqlite') as db:
#     pass  #створює базу (вперше)
#     conn = db.cursor()
#     conn.execute('CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT, name_product TEXT, price REAL, main_img TEXT, dop_img1 TEXT, dop_img2 TEXT)')
#     conn.commit()

def get_products():
    conn = get_conect_bd()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return products