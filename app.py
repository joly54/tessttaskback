import json
import random
import string

from flask import Flask, request, make_response, jsonify
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app, supports_credentials=True)
login_manager = LoginManager()
login_manager.init_app(app)

api = Api(app)
admin = Admin(app, template_mode='bootstrap4')

CORS(app, supports_credentials=True)
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_SAMESITE'] = 'None'
app.config['REMEMBER_COOKIE_SECURE'] = True
app.config['REMEMBER_COOKIE_HTTPONLY'] = True

app.config['TIMEZONE'] = 'Europe/Kiev'

app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['FLASK_ADMIN_FLUID_LAYOUT'] = True
app.config["SECRET_KEY"] = "secretkey"


def generate_token(length=80):
    characters = string.ascii_letters + string.digits
    token = ''.join(random.choice(characters) for _ in range(length))
    return token


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///base.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    surname = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(80), nullable=True)

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User %r>' % self.login


class laptop(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label = db.Column(db.String(1000))
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(1000), nullable=False)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)


class productView(ModelView):
    column_list = ("id", 'label', 'price', 'image')


class orderView(ModelView):
    column_list = ("id", 'user_id', 'product_id', 'total_price')


class userView(ModelView):
    column_list = ("id", 'login', 'email', 'password', 'name', 'surname', 'address')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


admin.add_view(productView(laptop, db.session))
admin.add_view(orderView(Order, db.session))
admin.add_view(userView(User, db.session))


@app.route('/')
def hello_world():
    return 'Hello World!'


class login(Resource):
    def post(self):
        data = request.data.decode('utf-8')
        data = json.loads(data)
        username = data['username']
        password = data['password']
        rememberMe = data['rememberMe']
        new_user = User.query.filter_by(login=username).first()
        if new_user is None:
            return {'Message': 'Invalid username or password'}, 403

        if new_user and new_user.password == password:
            login_user(new_user, remember=rememberMe)
            rest = {
                "message": "User logged in successfully",
            }
            return {'message': 'User logged in successfully'}, 200
        else:
            return {'Message': 'Invalid username or password'}, 403


class testCookie(Resource):
    def get(self):
        resp = make_response('Hello, World!', 200)
        resp.set_cookie('test', 'test', samesite='None', secure=True)
        return resp


api.add_resource(testCookie, '/testCookie')


class Register(Resource):
    def post(self):
        data = request.data.decode('utf-8')
        data = json.loads(data)
        username = data['username']
        password = data['password']
        email = data['email']
        name = data['name']
        surname = data['surname']
        new_user = User.query.filter_by(login=username).first()
        if new_user:
            return {"message": "User with this username already exists"}, 403
        new_user = User.query.filter_by(email=email).first()
        if new_user:
            return {"message": "User with this email already exists"}, 403
        if login == '' or password == '' or email == '' or name == '' or surname == '':
            return {"message": "Empty field"}, 403
        new_user = User(
            login=username,
            password=password,
            email=email,
            name=name,
            surname=surname
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        return {"message": "User created successfully"}, 200


class get_laptops(Resource):
    def get(self):
        #get page and size from qeury
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 10, type=int)
        products = laptop.query.paginate(page=page, per_page=size).items
        print(page, size)
        ans = []
        for product in products:
            ans.append({
                'id': product.id,
                'label': product.label,
                'price': product.price,
                'image': product.image
            })
        return jsonify(ans)



class user_info(Resource):
    def get(self):
        if not current_user.is_authenticated:
            return {'message': 'User not logged in'}, 403
        order = Order.query.filter_by(user_id=current_user.id).all()
        return {
            "message": "success",
            'login': current_user.login,
            'email': current_user.email,
            'name': current_user.name,
            'surname': current_user.surname,
            "address": current_user.address,
            'orders': [{
                'product_id': o.product_id,
                "product_name": laptop.query.filter_by(id=o.product_id).first().label,
                "product_price": laptop.query.filter_by(id=o.product_id).first().price,
                "product_image": laptop.query.filter_by(id=o.product_id).first().image,
                'total_price': o.total_price
            } for o in order]
        }, 200


class logout(Resource):
    def post(self):
        response = make_response({'message': 'User logged out'}, 200)
        #clear all user cookies
        for key in request.cookies:
            response.set_cookie(key, '', expires=0, samesite='None', secure=True)
        logout_user()

        return response

class update_user(Resource):
    def post(self):
        if not current_user.is_authenticated:
            return {'message': 'User not logged in'}, 403
        data = request.data.decode('utf-8')
        data = json.loads(data)
        email = data['email']
        name = data['name']
        surname = data['surname']
        address = data['address']
        user = User.query.filter_by(id=current_user.id).first()
        user.email = email
        user.name = name
        user.surname = surname
        user.address = address
        db.session.commit()
        return {"message": "User updated successfully"}, 200

class isUserLogged(Resource):
    def get(self):
        if current_user.is_authenticated:
            return {"message": "User logged in"}, 200
        else:
            return {"message": "User not logged in"}, 403


api.add_resource(logout, '/logout')
api.add_resource(get_laptops, '/products')
api.add_resource(login, '/login')
api.add_resource(Register, '/register')
api.add_resource(user_info, '/profile')
api.add_resource(update_user, '/update_user_data')
api.add_resource(isUserLogged, '/is_user_logged')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
