from flask import jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import app

@app.route('/dashboard')
@jwt_required()
def dashboard():
    return render_template('page/dashboardpage.html'), 200