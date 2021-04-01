import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
print('__file__={0:<35} | __name__={1:<20} | __package__={2:<20}'.format(__file__,__name__,str(__package__)))
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
db_drop_and_create_all()

## ROUTES

@app.route('/drinks',methods=['GET'])
def get_drinks():
    if request.method=="GET":
        # drink1=Drink(title="ewefwefe",recipe= '[{"color": "string", "name":"string", "parts":"number"}]')
        # drink1.insert()
        drinks=Drink.query.all()
        print(drinks)
        if drinks is not None:
            drinks =[drink.short() for drink in drinks]
        return jsonify({
            "success": True, 
            "drinks": drinks
            })

@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(JWT):
    print(request)
    body=request.get_json()
    title=body['title']
    items=['name','color','parts']
    for item in items :
        for comp in body['recipe']:
            if item not in comp.keys():
                abort(400)
    print(body['recipe'])
    recipe=json.dumps(body['recipe'])
    print(recipe)
    drink=Drink(title=title,recipe=recipe)
    try:
        drink.insert()
    except:
        abort(400)
    print("here")
    drink=Drink.query.filter(Drink.title==title).one()
    return jsonify({
       "success": True, 
       "drinks": drink.long()
       })  

        


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drink_details(JWT):
    # drink1=Drink(title="ewefwefe",recipe= '[{"color": "string", "name":"string", "parts":"number"}]')
    # drink1.insert()
    drinks=Drink.query.all()
    print(drinks)
    if drinks is not None:
        drinks =[drink.long() for drink in drinks]
    return jsonify({
        "success": True, 
        "drinks": drinks
        })




@app.route('/drinks/<int:id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drinks(JWT,id):
    print(request)
    arr=[]
    recipe=0
    title=0
    body=request.get_json()
    if 'title' in body.keys():
        title=body['title']
        print(title)
    if 'recipe'in body.keys():
        items=['name','color','parts']
        for item in items :
             if item not in body['recipe'].keys():
                 abort(400)
        recipe=json.dumps(body['recipe'])
        print(recipe)
    drink=Drink.query.get(id)
    if title:
        drink.title=title
    if recipe:
        drink.recipe=recipe    
    try:
        drink.update()
    except:
        abort(400)
    print("here")
    drink=Drink.query.get(id)
    print("updated drink= ")
    print(drink)
    arr.append(drink.long())
    return jsonify({
       "success": True, 
       "drinks": arr
       }) 


@app.route('/drinks/<int:id>',methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(JWT,id):
    print(request)
    drink=Drink.query.get(id)  
    try:
        drink.delete()
    except:
        abort(400)
    print("here")
    drink=Drink.query.filter(Drink.id ==id).one_or_none()
    if drink is not None:
        abort(400)
    return jsonify({
       "success": True, 
       "delete":id
       })

## Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(400)
def bad_request(error):
  return jsonify({
    "success": False, 
    "error": 400,
    "message": "bad request"
    }), 400  

@app.errorhandler(403)
def not_found(error):
  return jsonify({
    "success": False, 
    "error": 403,
    "message": "unauthorized"
    }), 403

@app.errorhandler(401)
def unprocessable(error):
  return jsonify({
    "success": False, 
    "error": 401,
    "message": "unauthorized"
    }), 401

@app.errorhandler(500)
def server_error(error):
  return jsonify({
    "success": False, 
    "error": 500,
    "message": "server error"
    }), 500

@app.errorhandler(AuthError)
def auth_error(error):
  return jsonify({
    "success": False, 
    "error": 401,
    "message": "Authorization error"
    }), 401