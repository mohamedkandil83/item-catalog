from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine

# ===================
# Database setup with user, catalog & item table
# The below script creates a
# .db file including the schema of the item catalog project
# ===================

Base = declarative_base()


# User Table
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    email = Column(String(256), nullable=False)
    picture = Column(String(512))

    @property
    def serialize(self):
        """Serializable User Instances"""
        return {
            'name': self.name,
            'id': self.id
        }


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="category")

    @property
    def serialize(self):
        """Serializable Category Instances"""
        return {
            'name': self.name,
            'id': self.id
        }


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    description = Column(String(256))
    picture = Column(String(512))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(
        Category,
        backref=backref('item', cascade='all, delete')
        )
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="item")

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description,
            'picture': self.picture,
            'category': self.category.name
        }


# engine = create_engine('sqlite:///final_catalog.db')

# Base.metadata.create_all(engine)
