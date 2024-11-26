from flask import Flask, render_template

import os

from models import init_db
from routes.home import home_bp
from user.login import login_bp
from user.registration import registration_bp
from user.logout import accaunt_bp
from user.accaunt import accaunts_bp
from shop.basket import basket_bp
from shop.like import like_bp
from admin.admin import admin_bp
from API.api import api_bp




app = Flask(__name__)
app.secret_key='GFihhIH934jHFGFD9jf80Mlk234MLGkln42hdvxcv'


init_db()


UPLOAD_FOLDER = os.path.join(os.getcwd(), 'Flask/static/img')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


app.register_blueprint(home_bp)
app.register_blueprint(login_bp)
app.register_blueprint(registration_bp)
app.register_blueprint(accaunt_bp)
app.register_blueprint(accaunts_bp)
app.register_blueprint(basket_bp)
app.register_blueprint(like_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(api_bp)




# def logout():
#     session.pop('user_id', None)  # Видаляємо дані користувача з сесії
#     session.pop('userinfo', None)  # Видаляємо ім'я користувача з сесії
#     flash('Ви вийшли з акаунта.')
    # return redirect(url_for('login_bp.login'))


@app.route('/recovery')
def recovery():
    return render_template('recovery.html')

@app.route('/recoverynumber')
def recoverynumber():
    return render_template('recoverynumber.html')










if __name__ == "__main__":
    app.run(debug=True)