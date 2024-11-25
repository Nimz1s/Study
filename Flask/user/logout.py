from flask import session, redirect, url_for, flash, Blueprint

accaunt_bp = Blueprint('accaunt_bp', __name__)

@accaunt_bp.route('/logout')
def logout():
    session.pop('user_id', None)  # Видаляємо дані користувача з сесії
    session.pop('userinfo', None)  # Видаляємо ім'я користувача з сесії
    flash('Ви вийшли з акаунта.')
    return redirect(url_for('login_bp.login'))