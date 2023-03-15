from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint,abort
from db import db
from models import StoreModel
from schemas import StoreSchema
from sqlalchemy.exc import SQLAlchemyError,IntegrityError

blp=Blueprint("Stores","stores",__name__,description="Operations on Stores")

@blp.route("/store/<int:store_id>") #based on store id 
class Store(MethodView):
    #get based on store id 
    @blp.response(200,StoreSchema) #in case of success how to return the response 
    def get(self,store_id):
        store = StoreModel.query.get_or_404(store_id) #get the item based on item id if not then 404 
        return store

    #delete the store based on store_id
    def delete(self,store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {"message": "Store deleted."},200

@blp.route("/store")

class Storelist(MethodView):
    #get list of store
    @blp.response(200, StoreSchema(many=True)) #in case of success how to return the response 
    def get(self): 
        return StoreModel.query.all() #return the list of stores 
    
    #add store to the system 
    @blp.arguments(StoreSchema) #add validation to store schema 
    @blp.response(200,StoreSchema) #in case of success 
    
    def post(self,store_data):
        store=StoreModel(**store_data) #break the dictionary to key word arguments - meaning to columns
        try:
            db.session.add(store) #add the item to DB
            db.session.commit() #commit the transaction
        except IntegrityError:  #make sure we don't have the same name again 
            abort(400,message="A store with the same name exists .")

        except SQLAlchemyError:
            abort(500,message="An Error occoured while inserting the Store to DB.")
        return store