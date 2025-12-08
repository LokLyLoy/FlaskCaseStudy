from app import app
from flask import render_template

@app.route('/about')
def about():
    return render_template('page/aboutpage.html')