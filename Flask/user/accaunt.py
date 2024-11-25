from flask import render_template, session, redirect, url_for, flash, Blueprint
from models import get_conect_bd

accaunts_bp = Blueprint('accaunt', __name__)

@accaunts_bp.route('/accaunt')
def accaunt():
    if 'user_id' not in session:
        flash('Ви не увійшли в акаунт.')
        return redirect(url_for('login_bp.login'))  # Перенаправлення на сторінку логіну, якщо не увійшли

    user_id = session['user_id']

    # Отримуємо дані користувача за user_id
    conn = get_conect_bd()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()

    if user:
        return render_template('accaunt.html', user=user)  # Передаємо інформацію про користувача в шаблон
    else:
        flash('Користувача не знайдено.')
        return redirect(url_for('login_bp.login'))