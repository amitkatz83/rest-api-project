#import uuid
#from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required,get_jwt #to protect the end points 
from schemas import ItemSchema,ItemUpdateSchema #import the schema validation
from db import db
from models import ItemModel
from sqlalchemy.exc import SQLAlchemyError

blp = Blueprint("Item", "item", description="Operations on items")

@blp.route("/item/<int:item_id>")
class Item(MethodView):
    @jwt_required() 
    #get item based on id
    @blp.response(200,ItemSchema) #in case of success serealize the response
    def get(self,item_id):
       item = ItemModel.query.get_or_404(item_id) #get the item based on item id if not then 404 
       return item

#delete item based on item id 
    #make sure we use username and password before use the endpoint
    @jwt_required() 
    def delete(self,item_id):
        jwt=get_jwt() #get gwt
        if not jwt.get("is_admin"):
            abort(401,message="Admin previlage is required")
        item = ItemModel.query.get_or_404(item_id) #get the item based on item id if not then 404 
        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted."}

#update Item based on item id 
    @blp.arguments(ItemUpdateSchema) #validation for update schema 
    @blp.response(200,ItemSchema) #in case of success 
    
    def put(self,item_data,item_id):
        item = ItemModel.query.get(item_id) #get the item based on item id if not then 404 
        if item: #mean the item exists in the db
            item.price=item_data["price"]
            item.name=item_data["name"]
        else:
            item=item_data(id=item_id,**item_data) #add new item to DB

        db.session.add(item)
        db.session.commit()
        return item

@blp.route("/item")

class Itemlist(MethodView):
    #make sure we use username and password before use the endpoint
    @jwt_required() 
    @blp.response(200,ItemSchema(many=True)) #in case of success how to return the response  
    #get all items 
    def get(self):
        return ItemModel.query.all() #return the list of stores 

    #make sure we use username and password before use the endpoint
    @jwt_required(refresh=True) #only refreshed token 
    #add item 
    @blp.arguments(ItemSchema) #to deal with import and schema validation
    @blp.response(201,ItemSchema) #in case of success how to return the response 
    
    def post(self, item_data): #validate that fields price + store_id + name
        item=ItemModel(**item_data) #break the dictionary to key word arguments - meaning to columns
        try:
            db.session.add(item) #add the item to DB
            db.session.commit() #commit the transaction
        except SQLAlchemyError:
            abort(500,message="An Error occoured while inserting the item to DB.")
        return item