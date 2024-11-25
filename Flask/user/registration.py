from flask import render_template, request, redirect, url_for, session, flash, Blueprint
from werkzeug.security import generate_password_hash
import sqlite3
from models import get_conect_bd


registration_bp = Blueprint('registration_bp', __name__)


@registration_bp.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        userinfo = request.form['userinfo']
        phonenumber = request.form['phone']
        email = request.form['email']
        password = request.form['password']


        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')


        conn = get_conect_bd()
        try:
            conn.execute('INSERT INTO users(userinfo, email, phonenumber, password, is_admin) VALUES (?, ?, ?, ?, ?)', (userinfo, email, phonenumber, hashed_password, 0))
            conn.commit()
            flash('Реєстрація успішна!')
            return redirect(url_for('login_bp.login'))
        except sqlite3.IntegrityError:
            flash('Це ім’я користувача вже зайняте. Виберіть інше.')
        finally:
            conn.close()

    return render_template('registration.html')