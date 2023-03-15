from db import db

class TagModel(db.Model):
    __tablename__ = "tags"
    #__table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    #foreign key to store
    store_id = db.Column(db.Integer(), db.ForeignKey("stores.id"), nullable=False)

    store = db.relationship("StoreModel", back_populates="tags")
    #connect to items tags
    items = db.relationship("ItemModel", back_populates="tags", secondary="items_tags")
