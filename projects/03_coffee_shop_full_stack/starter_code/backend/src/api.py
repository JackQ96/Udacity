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

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    all_drinks = Drink.query.all()
    drinks = [drink.short() for drink in all_drinks]

    if len(drinks)==0:
        abort(404)

    return jsonify({
        'Success': True,
        'drinks': drinks
    })

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    all_drinks = Drink.query.all()
    drinks = [drink.long() for drink in all_drinks]

    if len(drinks)==0:
        abort(404)

    return jsonify ({
        'Success': True,
        'drinks': drinks
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

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
            add_drink = Drink(title= title, recipe= json.dumps(recipe))
            add_drink.insert()

        return jsonify ({
            'Success': True,
            'drinks': add_drink.long()
        }),200

    except Exception as e:
      print(e)
      abort(422)




'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<id>', methods = ['PATCH'])
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
            updated_drink = Drink(title = title, recipe= json.dumps(recipe))
            updated_drink.update()
        
        return jsonify({
            'Success': True,
            'drinks': updated_drink.long()
        }),200
    
    except Exception as e:
      print(e)
      abort(422)

        




'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
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


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def notfound(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
