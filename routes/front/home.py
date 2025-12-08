from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from app import app
from flask import render_template
from products import product_list


@app.route('/')
def homepage():
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
    except:
        pass

    return render_template('page/homepage.html', products=product_list)
