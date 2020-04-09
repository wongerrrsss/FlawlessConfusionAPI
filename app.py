from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_heroku import Heroku
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.sqlite")

db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
heroku = Heroku(app)
CORS(app)

# SAVING THE USER INFO 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=True)
     # Since we didn't add the nullable field, the user does NOT have to have an email
    # I am adding the nullable field because it is REQUIRED for the user to enter an email 
    # in order to access the site

    def __init__(self, email, password):
        self.email = email
        self.password = password
        
class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "email", "password")

user_schema = UserSchema()
users_schema = UserSchema(many=True)

class AccountInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Integer, nullable=True,)
    email = db.Column(db.String(), nullable=True,  unique=True)
    address= db.Column(db.String(), nullable=True)
    city = db.Column(db.String(), nullable=True)
    state = db.Column(db.String(), nullable=True)
    zipcode = db.Column(db.String(), nullable=True)

    def __init__(self, name, email, address, city, state, zipcode):
        self.name = name
        self.email = email
        self.address = address
        self.city = city
        self.state = state
        self.zipcode = zipcode
        
class AccountInfoSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "address", "city", "state", "zipcode")

accountinfo_schema = AccountInfoSchema()
accountinfos_schema = AccountInfoSchema(many=True)

@app.route("/account/adduser", methods=["POST"])
# route may not work, may need to add custom <id> for each user?
def add_accountinfo():
    if request.content_type != "application/json":
        return jsonify("Error: Error must be sent as JSON data.")
    post_data = request.get_json()
    name = post_data.get("name")
    email = post_data.get("email")
    address = post_data.get("address")
    city = post_data.get("city")
    state = post_data.get("state")
    zipcode = post_data.get("zipcode")
    

    record = AccountInfo(name, email, address, city, state, zipcode)
    db.session.add(record)
    db.session.commit()

    return jsonify("Successfully updated account information!")

#POST for account info 
# start get request for account info

@app.route("/users/account", methods=["GET"])
def get_accountinfo():
    all_users = db.session.query(AccountInfo).all()
    return jsonify(accountinfo_schema.dump(AccountInfo))

@app.route("/account/get/by_id/<id>", methods=["GET"])
def get_accountinfo_by_id(id):
    user = db.session.query(AccountInfo).filter(AccountInfo.id == id).first()
    return jsonify(accountinfo_schema.dump(AccountInfo))
# end get request for account info

@app.route("/user/adduser", methods=["POST"])
def add_user():
    if request.content_type != "application/json":
        return jsonify("Error: Error must be sent as JSON data.")
    post_data = request.get_json()
    email = post_data.get("email")
    password = post_data.get("password")

    encrypted_password = bcrypt.generate_password_hash(password).decode("utf8")

    record = User(email, encrypted_password)
    db.session.add(record)
    db.session.commit()

    return jsonify("Successfully created user")

#ENDPOST

#PuT

@app.route("/users/update/<id>", methods=["PUT"])
def update_user(id): 
    if request.content_type == "application/json":
        put_data = request.get_json()
        password = put_data.get("password")

        user = db.session.query(User).filter(User.id == id).first()
        user.password = password
        db.session.commit()
        return jsonify("Password Updated")
    return jsonify("Error must be sent as JSON")

    #ENDPuT

#START GET for users

@app.route("/users/get", methods=["GET"])
def get_all_users():
    all_users = db.session.query(User).all()
    return jsonify(users_schema.dump(all_users))

@app.route("/users/get/by_id/<id>", methods=["GET"])
def get_user_by_id(id):
    user = db.session.query(User).filter(User.id == id).first()
    return jsonify(user_schema.dump(user))

@app.route("/users/get/by_email/<email>", methods=["GET"])
def get_user_by_email(email):
    user = db.session.query(User).filter(User.email == email.first())
    return jsonify(user_schema.dump(email))

#END GET of users

if __name__ == "__main__":
    app.debug = True
    app.run()