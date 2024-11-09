from flask import Flask, render_template, url_for, session
from models import init_db
from routes.home import home_bp
from routes.item import item_bp


app = Flask(__name__)

init_db()


app.register_blueprint(home_bp)
app.register_blueprint(item_bp)





@app.route('/like')
def like():
    return render_template('like.html')


@app.route('/basket')
def basket():
    return render_template('basket.html')


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/recovery')
def recovery():
    return render_template('recovery.html')

@app.route('/recoverynumber')
def recoverynumber():
    return render_template('recoverynumber.html')

@app.route('/registration')
def registration():
    return render_template('registration.html')


@app.route('/accaunt')
def accaunt():
    return render_template('accaunt.html')


if __name__ == "__main__":
    app.run(debug=True)