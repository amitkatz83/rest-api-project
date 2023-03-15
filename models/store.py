from db import db
class StoreModel(db.Model):
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    tags = db.relationship("TagModel", back_populates="store", lazy="dynamic")
    items = db.relationship("ItemModel", back_populates="store", lazy="dynamic") #define relationship between store ans item. 
    #we don't fetch item if not asked in case data is delete from store then entire items from store deleted  cascade="all, delete"
