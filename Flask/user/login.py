from flask import render_template, request, redirect, url_for, session, flash, Blueprint
from werkzeug.security import check_password_hash
from models import get_conect_bd
import sqlite3


login_bp = Blueprint('login_bp', __name__)


@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_conect_bd()
        cursor = conn.cursor()
        
        # Отримання інформації про користувача за email
        user = cursor.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['email'] = user['email']
            is_admin = bool(user['is_admin'])  # Перевірка статусу адміністратора
            
            # Встановлення додаткових прав, якщо користувач — адміністратор
            if is_admin:
                session['is_admin'] = True
                flash("Ви увійшли як адміністратор")
            else:
                session['is_admin'] = False
                flash("Ви увійшли як звичайний користувач")
            
            conn.close()
            return redirect(url_for('accaunt.accaunt'))  # Перехід до сторінки акаунта
            
        else:
            flash("Логін або пароль невірний")
            conn.close()

    return render_template('login.html')



# @login_bp('/logout')
# def logout():
#     session.clear()
#     flash('Ви вийшли із системи')
#     return redirect(url_for('/home'))