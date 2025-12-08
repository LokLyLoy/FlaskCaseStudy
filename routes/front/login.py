from flask import render_template

from app import app

@app.route('/login')
def loginPage():
    return render_template('page/loginpage.html'), 200