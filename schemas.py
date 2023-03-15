from marshmallow import Schema,fields
#dump only usually for keys

#to make sure the fields are there when we create item 
class PlainItemSchema(Schema):
    id=fields.Int(dumpy_only=True) #means to return data from the api and not nesscary in json payload
    name=fields.Str(required=True) #we recieve name in the json payload, its required
    price=fields.Float(required=True) #we recieve name in the json payload, its required

#plain store 
class PlainStoreSchema(Schema):
    id=fields.Int(dumpy_only=True) #means to return data from the api and not nesscary in json payload
    name=fields.Str() #we recieve name in the json payload, its required


class PlainTagSchema(Schema):
    id=fields.Int(dumpy_only=True) #means to return data from the api and not nesscary in json payload
    name=fields.Str() #we recieve name in the json payload, its required


#nested item with store
class ItemSchema(PlainItemSchema):
    store_id = fields.Int(required=True, load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)

#to make sure the fields are there but no required when updating Item 
class ItemUpdateSchema(Schema):
    name=fields.Str() #field is optional
    price=fields.Float() #field is optional
    store_id=fields.Int() #field is optional

#store with Store to be related with item and tag
class StoreSchema(PlainStoreSchema):
    items=fields.List(fields.Nested(PlainItemSchema()),dump_only=True)
    tags=fields.List(fields.Nested(PlainTagSchema()),dump_only=True)

#create the Tag Schema 
class TagSchema(PlainTagSchema):
    store_id = fields.Int(load_only=True)
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)

#define the relationship between tag and items - many to many 
class TagAndItemSchema(Schema):
    message = fields.Str()
    item = fields.Nested(ItemSchema)
    tag = fields.Nested(TagSchema)

#class for the users 
class UserSchema(Schema):
    id = fields.Int(dump_only=True) #means to return data from the api and not nesscary in json payload
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True) #we will not return the password to the API and should not be saved