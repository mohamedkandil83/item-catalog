from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy_utils import database_exists, drop_database, create_database

from database_setup import Category, User, Base, Item

engine = create_engine('sqlite:///final_catalog.db')

# Clear & re-create
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create a user
user1 = User(name="Mohamed Kandil", email="mohamedkandil83@gmail.com",
             picture='http://2.bp.blogspot.com/-u54XGk-hUdU/U1zanJgulMI/AAAAAAAAByM/aKk9EDRONLc/s1600/blogbuzz_logo.gif')
session.add(user1)
session.commit()

# Football category and its teams
category1 = Category(name="Football Teams", user_id=1)

session.add(category1)
session.commit()

item1 = Item(name="Real madrid", user_id=1, description="The best in spain", category=category1,picture='https://thumbs.dreamstime.com/thumblarge_2160/21608473.jpg')

session.add(item1)
session.commit()

item2 = Item(name="Arsenal", user_id=1,  description="It usedto be the best in England.", category=category1,picture='https://thumbs.dreamstime.com/thumblarge_2160/21608473.jpg')

session.add(item2)
session.commit()

item3 = Item(name="Bayern", user_id=1, description="The king of Germany", category=category1,picture='https://thumbs.dreamstime.com/thumblarge_2160/21608473.jpg')

session.add(item3)
session.commit()

item3 = Item(name="AC Milan", user_id=1, description="The Arsenal of Italy", category=category1,picture='https://thumbs.dreamstime.com/thumblarge_2160/21608473.jpg')

session.add(item3)
session.commit()

# Countries
category2 = Category(name="Countries", user_id=1)

session.add(category2)
session.commit()

item1 = Item(name="Turkey", user_id=1, description="Asia & Europe", category=category2,picture='https://thumbs.dreamstime.com/thumblarge_2160/21608473.jpg')

session.add(item1)
session.commit()

item2 = Item(name="Egypt", user_id=1,  description="Africa & Asia", category=category2,picture='https://thumbs.dreamstime.com/thumblarge_2160/21608473.jpg')

session.add(item2)
session.commit()


# Cars
category3 = Category(name="Cars", user_id=1)

session.add(category3)
session.commit()

item1 = Item(name="Mercedes", user_id=1, description="The elite", category=category3,picture='https://thumbs.dreamstime.com/thumblarge_2160/21608473.jpg')

session.add(item1)
session.commit()

item2 = Item(name="Audi", user_id=1, description="THE richie", category=category3,picture='https://thumbs.dreamstime.com/thumblarge_2160/21608473.jpg')

session.add(item2)
session.commit()

item3 = Item(name="Tesla", user_id=1, description="For kids", category=category3,picture='https://thumbs.dreamstime.com/thumblarge_2160/21608473.jpg')

session.add(item3)
session.commit()

# others
category4 = Category(name="Other", user_id=1)

session.add(category4)
session.commit()


items = session.query(Item).all()
for item in items:
    print "Item: " + item.name +","+item.category.name