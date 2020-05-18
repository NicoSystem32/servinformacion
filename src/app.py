from flask import Flask , request , jsonify , Response , make_response
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash,check_password_hash
from bson import json_util
from bson.objectid import ObjectId
import jwt
import datetime
from functools import wraps
import utilities


app = Flask(__name__)
app.config['SECRET_KEY'] = 'estaeslallavesecreta'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/RegistroVotos'
mongo = PyMongo(app)

def tokenrequire(f):
    @wraps(f)
    def decorated(*args,**kwarts):
        token = request.args.get('token')
        if not token:
            return jsonify({'message':'El token no es válido'}),403
        try:
            data = jwt.decode(token,app.config['SECRET_KEY'])
        except:
            return jsonify({'message':'El token caducó =( debes volver a logearte !'}), 403
        return (f(*args,**kwarts))
    return decorated

@app.route('/actualizalider/<id>' , methods = ['PUT'])
def update_lid(id):
    username = request.json['username']
    password = request.json['password']
    nombres = request.json['nombres']
    apellidos = request.json['apellidos']
    celular = request.json['celular']
    rol = request.json['rol']
    email = request.json['email']
    usuariocreador = request.json['usuariocreador']
    

    onlyadm = mongo.db.ADMINISTRADORES.find_one({'usuario': usuariocreador})
    if(onlyadm == None):
        onlyadm = {'usuario': ''} 
    if(onlyadm['usuario'] == usuariocreador):
        if (username and password and nombres and apellidos and celular and rol and email and usuariocreador):
            passhased = generate_password_hash(password)

            id = mongo.db.LIDERES.update_one({'_id': ObjectId(id)}, {'$set': {
                    'username':username,
                    'password':passhased,
                    'nombres' :nombres,
                    'apellidos' : apellidos,
                    'celular' : celular,
                    'rol' : rol,
                    'email':email,
                    'usuariocreador' : usuariocreador
            }})
            response = {
                    'id':str(id),
                    'username':username,
                    'email':email,
                    'message':" Actualizado correctamente ! =)"

            }
            return response
        else:
            error = {
                'message' : 'No se pudo crear el usuario =( seguro te falto alguno, verifica los datos !'
            }
            return error
    else:
        error = {'message': 'Solamente los usuarios adm pueden actualizar data  = |'}
        return error
    

@app.route('/votantes', methods = ['POST'])
@tokenrequire
def autorizado():
    

    return jsonify({'message':'Solamente válido con token'})

@app.route('/login', methods = ['GET'])
def login():
    username = request.json['username']
    password = request.json['password']
    count_useradmin = mongo.db.ADMINISTRADORES.find({"usuario": username}).count()
    count_userlider = mongo.db.LIDERES.find({"usuario": username}).count()
        
    if(count_useradmin == 0 and count_userlider == 0):
    
        return jsonify(response = {'message' : 'El usuario no existe =V '})
    
    elif(count_useradmin == 1):
    
        users = mongo.db.ADMINISTRADORES.find_one({"usuario": username})
        us = (users["usuario"])
        ky = (users['password'])
        rl = (users['rol'])
        
        if us == username and ky == password:
            token = jwt.encode({'user': username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=2)}, app.config['SECRET_KEY'])
            return jsonify({'login como': rl ,'token': token.decode('UTF-8')})
        return make_response('No se pudo verificar =(',401,{'www-Authenticate':'Basic realm="Necesita hacer login nuevamente"'})

        
    
    elif(count_userlider == 1):
    
        usersl = mongo.db.LIDERES.find_one({"usuario": username})
        
        
        us = (usersl["usuario"])
        ky = (usersl['password'])
        rl = (usersl['rol'])
        print(us == username and ky == password)
        if us == username and ky == password:
            token = jwt.encode({'user': username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=2)}, app.config['SECRET_KEY'])
            return jsonify({'login como': rl ,'token': token.decode('UTF-8')})
        return make_response('No se pudo verificar =(',401,{'www-Authenticate':'Basic realm="Necesita hacer login nuevamente"'})
        
    else:
        pass
    return rl

@app.route('/registrolideres',methods= ['POST'])
@tokenrequire
def insert_lid():
    username = request.json['username']
    password = request.json['password']
    nombres = request.json['nombres']
    apellidos = request.json['apellidos']
    celular = request.json['celular']
    rol = request.json['rol']
    email = request.json['email']
    usuariocreador = request.json['usuariocreador']
    print(usuariocreador)

    onlyadm = mongo.db.ADMINISTRADORES.find_one({'usuario': usuariocreador})
    if(onlyadm == None):
        onlyadm = {'usuario': ''} 
    if(onlyadm['usuario'] == usuariocreador):
        if (username and password and nombres and apellidos and celular and rol and email and usuariocreador):
            passhased = generate_password_hash(password)

            id = mongo.db.LIDERES.insert({
                    'username':username,
                    'password':passhased,
                    'nombres' :nombres,
                    'apellidos' : apellidos,
                    'celular' : celular,
                    'rol' : rol,
                    'email':email,
                    'usuariocreador' : usuariocreador
            })
            response = {
                    'id':str(id),
                    'username':username,
                    'email':email,
                    'message':f"Creado correctamente por {usuariocreador}  =)"

            }
            return response
        else:
            error = {
                'message' : 'No se pudo crear el usuario =( seguro te falto alguno, verifica los datos !'
            }
            return error
    else:
        error = {'message': 'Solamente los usuarios adm pueden crear usuarios  = |'}
        return error



if __name__ == "__main__":
    app.run(debug = True )