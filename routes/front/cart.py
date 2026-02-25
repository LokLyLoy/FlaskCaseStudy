from flask import render_template

from app import app

@app.route('/cart')
def cartPage():
    return render_template("page/cartpage.html")