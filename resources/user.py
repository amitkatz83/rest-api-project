import os
from flask.views import MethodView
from flask_smorest import Blueprint,abort
from sqlalchemy.exc import SQLAlchemyError
from passlib.hash import pbkdf2_sha256 #for hash algorithm to hash the password
from db import db
from models.user import UserModel
from schemas import UserSchema,UserRegisterSchema
from flask_jwt_extended import (create_access_token,create_refresh_token,get_jwt_identity,
                                get_jwt,jwt_required) #for tokens 
from sqlalchemy import or_
from blocklist import BLOCKLIST #import blocklist for saving the token
import requests

blp=Blueprint("Users","users",description="Operations on users")

def send_simple_message(to, subject, body):
    domain = os.getenv("MAILGUN_DOMAIN")
    return requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", os.getenv("MAILGUN_API_KEY")),
        data={
            "from": f"Your Name <mailgun@{domain}>",
            "to": [to],
            "subject": subject,
            "text": body,
        },
    )


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema)
    def post(self, user_data):
        if UserModel.query.filter
        or_(
        (UserModel.username == user_data["username"],
         UserModel.email==user_data["email"])
         ).first():
            abort(409, message="A user with that username or email already exists.")

        user = UserModel(
            username=user_data["username"],
            email=user_data["email"],
            password=pbkdf2_sha256.hash(user_data["password"]),
        )
        db.session.add(user)
        db.session.commit()

        send_simple_message(to=user.email,
                            subject="Sucessfully Signed Up",
                            body=f"Hi {user.username}! You have successfully signed up to the Store REST API")

        return {"message": "User created successfully."}, 201

#refresh token 
@blp.route("/refresh") #refreshing the token
class TokenRefresh(MethodView):
    @jwt_required(refresh=True) #to get only fresh token
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        #if we want to have one fresh token only 
        #jti=get_jwt()["jti"]
        #BLOCKLIST.add(jti)
        return {"access_tocken": new_token},200
    

@blp.route("/login") #end point to deal with the login
class userLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self,user_data): #its post since we send data to the end point 
        user=UserModel.query.filter(UserModel.username==user_data["username"]).first() #check if the username is the same as the username in the DB

        if user and pbkdf2_sha256.verify(user_data["password"],user.password): #check if there is username (not none) and the password is correct against the DB

            #create access token where the identity is based on the id
            access_token=create_access_token(identity=user.id,fresh=True)
            #create refresh token
            refresh_token=create_refresh_token(identity=user.id)

            return {"access_token": access_token,"refresh_token": refresh_token}

        abort(401,message="Invalid credentials.") #not valid password 

#handeling log out
@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required() #grab the blocklist
    def post(self):
        jti = get_jwt()["jti"]  #same as get_jwt().get("jti")
        BLOCKLIST.add(jti) #add the token it to blocklist 
        return {"message": "Successfully logged out"}, 200


@blp.route("/user/<int:user_id>") #get user name based on the id 
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id): #get the users
        user = UserModel.query.get_or_404(user_id)
        return user

    def delete(self, user_id): #delete user
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted."}, 200