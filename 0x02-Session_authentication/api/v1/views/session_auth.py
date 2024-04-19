#!/usr/bin/env python3
"""Module contains views for handling session authentication"""


from api.v1.views import app_views
from flask import abort, jsonify, request
from models.user import User
import os


@app_views.route('/auth_session/login', methods=['POST'], strict_slashes=False)
def login():
    """
    POST/api/v1/auth_session/login
    """
    email = request.form.get('email')
    password = request.form.get('password')
    if email is None or "":
        return jsonify({"error": "email missing"}), 400
    if password is None or "":
        return jsonify({"error": "password missing"}), 400
    users = User.search({"email": email})
    if len(users) == 0:
        return jsonify({"error": "no user found for this email"})
    for user in users:
        if not User.is_valid_password(user, password):
            return jsonify({"error": "wrong password"}), 401

        from api.v1.app import auth
        session_id = auth.create_session(user.id)
        response = jsonify(user.to_json())
        cookie_name = os.getenv('SESSION_NAME')
        response.set_cookie(cookie_name, session_id)
        return response


@app_views.route('/auth_session/logout',
                 methods=['DELETE'], strict_slashes=False)
def logout():
    """
    DELETE /api/v1/auth_session/logout
    """
    from api.v1.app import auth
    if not auth.destroy_session(request):
        abort(404)
    return jsonify({}), 200
