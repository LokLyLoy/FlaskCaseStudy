from flask import request, jsonify, make_response, redirect
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from werkzeug.security import check_password_hash

from app import app, jwt
from model import User

REVOKE_JTIS = set()
jwt_blocklist = set()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in jwt_blocklist

@app.post("/login")
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Please provide username and password"}), 400

    user = User.query.filter(User.username == username).first()

    if not user:
        return jsonify({"message": "incorrect username or password"}), 401

    user_id = str(user.id)
    password_match = check_password_hash(user.password, password)

    if password_match:
        access_token = create_access_token(identity=user_id)
        res = jsonify({"message": "success" ,"access_token": access_token})

        res.set_cookie(
            "access_token",
            access_token,
            httponly=True,
            secure=False,
            samesite="Lax",
        )
        print(user_id)
        return res
    else:
        return jsonify({"message": "incorrect username or password"}), 401


@app.post("/logout")
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    jwt_blocklist.add(jti)

    res = make_response(redirect('/'))
    res.set_cookie(
        "access_token",
        expires=0,
        httponly=True,
        secure=False,
        samesite="Lax",
    )
    return jsonify({"message": "logout successful"}), 200
