from flask import render_template, Blueprint, redirect, url_for, session, flash
from models import get_conect_bd


like_bp = Blueprint('like_bp', __name__)

@like_bp.route('/add/<int:item_id>', methods=['POST'])
def add_to_like(item_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('Будь ласка, увійдіть в акаунт, щоб додати в обране')
        return redirect(url_for('login_bp.login'))
    
    conn = get_conect_bd()
    # Перевіряємо, чи товар вже є в обраному
    existing_item = conn.execute('SELECT * FROM likes WHERE user_id = ? AND item_id = ?', (user_id, item_id)).fetchone()
    if not existing_item:
        conn.execute('INSERT INTO likes(user_id, item_id) VALUES (?, ?)', (user_id, item_id))
        conn.commit()
        flash('Товар додано до обраного')
    else:
        flash('Товар вже є в обраному')
    conn.close()
    return redirect(url_for('like_bp.show_likes'))

@like_bp.route('/like')
def show_likes():
    user_id = session.get('user_id')
    if not user_id:
        flash('Будь ласка, увійдіть в акаунт, щоб переглянути обране')
        return redirect(url_for('login_bp.login'))
    
    conn = get_conect_bd()
    # Отримуємо обрані товари для поточного користувача
    items = conn.execute('''
        SELECT products.id, products.name_product, products.price, products.main_img
        FROM products
        JOIN likes ON products.id = likes.item_id
        WHERE likes.user_id = ?
    ''', (user_id,)).fetchall()
    conn.close()
    
    return render_template('like.html', items=items)


@like_bp.route('/remove_from_like/<int:item_id>', methods=['POST'])
def remove_from_like(item_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('Будь ласка, увійдіть в акаунт, щоб видалити товари з кошика')
        return redirect(url_for('login_bp.login'))
    
    conn = get_conect_bd()
    conn.execute('DELETE FROM likes WHERE user_id = ? AND item_id = ?', (user_id, item_id))
    conn.commit()
    conn.close()
    flash('Товар видалена із обраного')
    return redirect(url_for('like_bp.show_likes'))