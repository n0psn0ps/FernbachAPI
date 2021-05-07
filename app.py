from flask import Flask, request, jsonify, make_response, render_template_string, url_for, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
### PyJWT-1.7.1 works with the JWT EXP ###
import jwt
import datetime
from functools import wraps
import os
from os import popen
import urllib

app = Flask(__name__)

app.config['SECRET_KEY'] = "supersecretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)

class Ship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(50))
    cc = db.Column(db.String(50))
    add = db.Column(db.String(50))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is missing.'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message' : 'Token is invald.'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

### SSTI Cloaked into the status page ####
@app.route("/status") ### user string:name + apply to response in resp.header with an if else
def home2():
    #if request.args.get('user'):
        return jsonify({"Welcome to" : "Fernbach's greatest invention!", "status of API" : "up and running"})

@app.route("/status/<string:a>") ### user string:name + apply to response in resp.header with an if else
def home(a):
    #if request.args.get('user'):
        return jsonify({"Welcome to" : "Fernbach's greatest invention!", "status of API" : "up and running" + render_template_string(a)})



#### MFLAC for depreciated ADMIN Panel ####

@app.route('/api/v0/admin', methods=['GET'])
@token_required
def all_users(current_user):
    users = User.query.all()

    output = []

    for user in users:
        user_data = {}
        user_data ['public_id'] = user.public_id
        user_data ['name'] = user.name
        user_data ['password'] = user.password
        user_data ['admin'] = user.admin
        output.append(user_data)

    return jsonify({'users' : output})

#### 

@app.route('/api/v1/user', methods=['GET'])
@token_required
def get_all_users(current_user):

    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that action.'})

    users = User.query.all()

    output = []

    for user in users:
        user_data = {}
        user_data ['public_id'] = user.public_id
        user_data ['name'] = user.name
        user_data ['password'] = user.password
        user_data ['admin'] = user.admin
        output.append(user_data)

    return jsonify({'users' : output})
### Fix this Endpoint No Longer Allowing a single user to run IDOR####
@app.route('/api/v1/user/<public_id>', methods=['GET'])
@token_required
def get_one_user(current_user, public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message' : 'No user found!'})
    
    user_data = {}
    user_data ['public_id'] = user.public_id
    user_data ['name'] = user.name
    user_data ['password'] = user.password
    user_data ['admin'] = user.admin
    
    return jsonify({'user' : user_data})

@app.route('/api/v1/user', methods=['POST'])
@token_required
def create_user():
"""
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that action. Need username and password parameters.'})
"""
    data = request.get_json()
### Change the hashing type? MD5 ####
    hashed_password = generate_password_hash(data['password'], method='md5')
### Use a guessable UUID that is not random but auto increments ####
    new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message' : 'New user created!'})

### Entry Point into admin functionality - MFLAC on endpoint ####
@app.route('/api/v1/user/<public_id>', methods=['PUT'])
@token_required
def promote_user(current_user, public_id):

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message' : 'No user found!'})

    user.admin = True
    db.session.commit()
    return jsonify({'message' : 'The user has been promoted'})
"""
@app.route('/api/v1/user/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):

    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that action.'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message' : 'No user found!'})

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message' : 'User has been deleted.'})
"""
### SQL injection vulnerability will live here ####

@app.route('/api/v1/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('No credentials supplied', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return make_response('Could not verify username or password', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id' : user.public_id, 'name' : user.name, 'password' : user.password, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=800)}, app.config['SECRET_KEY'])

        return jsonify({'token' : token.decode('UTF-8')})

    return make_response('Could not verify password', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

### Package Shipments API endpoints ###
@app.route('/shipments', methods=['GET'])
@token_required
def get_all_shipments(current_user):

    if not current_user.admin:
        return jsonify({'message' : 'Admin privileges required. Cannot perform that action.'})

    shipments = Ship.query.filter_by(user_id=current_user.id).all()
    
    output = []

    for ship in shipments:
        ship_data = {}
        ship_data['id'] = ship.id
        ship_data['product'] = ship.product
        ship_data['cc'] = ship.cc
        ship_data['add'] = ship.add
        ship_data['complete'] = ship.complete
        ship_data['user_id'] = ship.user_id
        output.append(ship_data)

    return jsonify({'shipments' : output})
### SSRF ####
### fix the blank issue with error log ###
@app.route('/api/v0/server', methods = ['GET'])
def ssrf():
    url = request.args.get("url")
    comp = ''
    cond1 = 'http://localhost'
    cond2 = 'http://localhost:80'
    cond3 = 'file:///etc/passwd'
    cond4 = 'http://google.com'
    if request.method == 'GET' and url == comp:
        return jsonify({'message' : 'No shipment found include a valid url.'})        
    elif request.method == 'GET' and url == cond1 or url == cond2 or url == cond3 or url == cond4:
        return urllib.request.urlopen(url).read() 
    else:
        return jsonify({'message' : 'No shipment found include a valid url.'})
### IDOR for todo > soon to be reciept items #### 
@app.route('/shipment/<ship_id>', methods=['GET'])
def get_one_todo(ship_id):
    ship = Ship.query.filter_by(id=ship_id).first()

    if not ship:
        return jsonify({'message' : 'No shipment found!'})

    ship_data = {}
    ship_data['id'] = ship.id
    ship_data['product'] = ship.product
    ship_data['cc'] = ship.cc
    ship_data['add'] = ship.add
    ship_data['complete'] = ship.complete
    ship_data['user_id'] = ship.user_id
    
    return (ship_data)
"""
@app.route('/shipment', methods=['POST'])
@token_required
def create_shipment(current_user):
    data = request.get_json()

    if not current_user.admin:
        return jsonify({'message' : 'Admin privileges required. Cannot perform that action.'})

    new_ship = Ship(product=data['product'], cc=data['cc'], add=data['add'], complete=False, user_id=current_user.id)
    db.session.add(new_ship)
    db.session.commit()

    return jsonify({'message' : "Shipment created!"})

@app.route('/shipment/<ship_id>', methods=['DELETE'])
@token_required
def delete_shipment(current_user, ship_id):
    ship = Ship.query.filter_by(id=ship_id, user_id=current_user.id).first()
    
    if not current_user.admin:
        return jsonify({'message' : 'Admin privileges required. Cannot perform that action.'})

    if not todo:
        return jsonify({'message' : 'No shipment found!'})
    
    db.session.delete(ship)
    db.session.commit()
    
    return jsonify({'message' : 'Shipment deleted.'})
"""
### Command Injection ###
@app.route('/api/v0/usage')
def ping():
    a = request.args.get("a")
    cmd = "uptime %s" % a
    os.popen(cmd)
    return popen(cmd).read()

### File Include and XXE? ###

@app.route("/api/v0/search")
def start():
    return render_template("warehouse.xml")

if __name__ == '__main__':
    app.run(debug=True)
