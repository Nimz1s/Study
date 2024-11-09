from flask import Blueprint, render_template


item_bp = Blueprint('item', __name__)

@item_bp.route('/item')
def item():
    return render_template('item.html')