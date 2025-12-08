from app import app
from flask import render_template, abort

@app.route('/abort404')
def abort404():
    abort(404)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('/error/404.html'), 404

@app.route('/crash')
def crash():
    abort(404)