from flask import render_template

from app import app

@app.route('/register')
def registerPage():
    return render_template("page/registerpage.html"), 200