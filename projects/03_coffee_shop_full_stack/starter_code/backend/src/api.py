import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


# db_drop_and_create_all()

# ROUTES

@app.route('/drinks', methods=['GET'])
def get_drinks():
    all_drinks = Drink.query.all()
    drinks = [drink.short() for drink in all_drinks]

    if len(drinks) == 0:
        abort(404)

    return jsonify({
        'Success': True,
        'drinks': drinks
    })


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    all_drinks = Drink.query.all()
    drinks = [drink.long() for drink in all_drinks]

    if len(drinks) == 0:
        abort(404)

    return jsonify({
        'Success': True,
        'drinks': drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    new_drink = request.get_json()

    title = new_drink.get('title')
    recipe = new_drink.get('recipe')

    try:
        if ((title is None) or (recipe is None)):
            abort(422)

        else:
            add_drink = Drink(title=title, recipe=json.dumps(recipe))
            add_drink.insert()

        return jsonify({
            'Success': True,
            'drinks': add_drink.long()
        }), 200

    except Exception as e:
        print(e)
        abort(422)


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def alter_drinks(payload, id):
    alter_drink = request.get_json()

    title = alter_drink.get('title')
    recipe = alter_drink.get('recipe')
    drink = Drink.query.get(id)

    try:
        if drink is None:
            abort(404)

        else:
            updated_drink = Drink(title=title, recipe=json.dumps(recipe))
            updated_drink.update()

        return jsonify({
            'Success': True,
            'drinks': [updated_drink.long()]
        }), 200

    except Exception as e:
        print(e)
        abort(422)


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    drink = Drink.query.get(id)

    if drink is None:
        abort(404)

    drink.delete()

    return jsonify({
        'success': True,
        'deleted': id
    })


# Error Handling

@app.errorhandler(AuthError)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(404)
def notfound(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404


@app.errorhandler(AuthError)
def badrequest(error):
    return jsonify({
                    "success": False,
                    "error": 400,
                    "message": "Bad Request"
                    }), 400


@app.errorhandler(AuthError)
def unauthorized(error):
    return jsonify({
                    "success": False,
                    "error": 401,
                    "message": "Bad Request"
                    }), 401
