import uuid

from flask import jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from app import app, db
from model import User

UPLOAD_FOLDER = 'static/avatars/'

@app.get('/users/list')
def users_list():
    users = User.query.all()

    result = [{
        'id': u.id,
        'username': u.username,
        'email': u.email,
    } for u in users]

    return jsonify(result), 200

@app.get('/users/<int:id>')
def users(id):
    user = User.query.get(id)

    if not user:
        return jsonify({"message": "user not found"}), 404

    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
    }), 200

@app.post('/users/create')
def users_create():
    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"message": "missing required filed"}), 400

    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()

    if existing_user:
        return jsonify({"message": "user already exists"}), 409

    hashed_password = generate_password_hash(password)

    new_user = User(
        username=username,
        email=email,
        password=hashed_password,
        avatar="FallBack.jpg"
    )

    db.session.add(new_user)
    db.session.commit()

    access_token = create_access_token(identity=new_user.id)

    res = jsonify({
        "message": "user created successfully",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "avatar": new_user.avatar,
        }
    })

    res.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=False,
        samesite="Lax",
    )

    return res, 200

@app.put('/users/update/<int:id>')
def users_update(id):
    user = User.query.get(id)

    if not user:
        return jsonify({"message": "user not found"}), 404

    data = request.get_json()
    user.username = data.get("username", user.username)
    user.email = data.get("email", user.email)
    new_password = data.get("password")

    if new_password:
        user.password = generate_password_hash(new_password)


    db.session.commit()

    return jsonify({
        "message": "user updated",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "password": user.password,
        }
    }), 200

@app.delete('/users/delete/<int:id>')
def users_delete(id):
    user = User.query.get(id)

    if not user:
        return jsonify({"message": "user not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({
        "message": "user deleted",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
    }), 200

@app.post('/me')
@jwt_required()
def me():
    user_id = get_jwt_identity()

    user_data = User.query.get(user_id)
    return jsonify({
        "user": {
            "id": user_data.id,
            "username": user_data.username,
            "email": user_data.email,
            "avatar": user_data.avatar
        }
    }), 200

@app.post('/user-profile')
@jwt_required()
def user_profile():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    if not current_user:
        return jsonify({"message": "user not found"}), 404

    if 'profile' not in request.files:
        return jsonify({"message": "missing required filed"}), 400

    file = request.files['profile']

    if file.filename == '':
        return jsonify({"message": "missing required filed"}), 400

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file.save(f"{UPLOAD_FOLDER}/{unique_filename}")
        current_user.avatar = unique_filename

    db.session.commit()

    return jsonify({
        "message": "user profile updated",
        "user": {
            "avatar": current_user.avatar,
        }
    }), 200
