from flask import Flask, redirect, url_for, jsonify,render_template,request
from flask import session as user_session
from flask_oauth import OAuth
from urllib2 import Request, urlopen, URLError
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
import json

# https://code.google.com/apis/console
GOOGLE_CLIENT_ID = '784859935364-03l0ofenuodrongl54fi6kua606onf9e.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'lkOxBobk10_KeRH12R63JZCz'
REDIRECT_URI = '/oauth2callback'  # one of the Redirect URIs from Google APIs console
 
SECRET_KEY = 'development key'
DEBUG = True
 
app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()

# database connection
engine = create_engine('sqlite:///final_catalog.db',)
Base.metadata.bind = engine
# session creation
DBSession = sessionmaker(bind=engine)
session = DBSession()
#print session


google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=GOOGLE_CLIENT_ID,
                          consumer_secret=GOOGLE_CLIENT_SECRET)
 
@app.route('/')
def index():
    access_token = user_session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))
 
    access_token = access_token[0]
 
    headers = {'Authorization': 'OAuth '+access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    try:
        res = urlopen(req)
    except URLError, e:
        if e.code == 401:
            # Unauthorized - bad token
            user_session.pop('access_token', None)
            return redirect(url_for('login'))
        return res.read()
 
    user_session['user'] = json.load(res)
    categories = session.query(Category).all()
    return render_template('header.html',user_session=user_session,categories=categories)
 

@app.route('/showCategory')
def showCategory():
    categories = session.query(Category).all()
    category_id = id=request.args.get('category_id')
    items = session.query(Item).filter_by(category_id=category_id).all()
    return render_template('header.html', items=items,
    user_session=user_session,
    categories=categories)
	
	
@app.route('/login')
def login():
	access_token = user_session.get('access_token')
	if access_token is not None:
		return "Welcome!!"
	callback=url_for('authorized', _external=True)
	return google.authorize(callback=callback)
 


#===================
# JSON End Point
#===================

@app.route('/api/catalog.json')
def showAllCatalogJSON():
    """Returns the whole catalog in json"""
    items = session.query(Item).order_by(Item.category_id)
    return jsonify(Items=[i.serialize for i in items])

@app.route(
    '/api/item/<int:item_id>.json')
def catalogItemJSON(item_id):
    """Returns an item in json"""
    item = session.query(
        Item).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)

@app.route(
    '/api/category/<int:category_id>.json')
def catalogCategoryJSON(category_id):
    """Returns a certain category in json"""
    category = session.query(
        Item).filter_by(id=category_id).one()
    return jsonify(Category=category.serialize)

@app.route(
    '/api/category/<int:category_id>/items.json')
def catalogCategoryItemsJSON(category_id):
    """Returns Items in a certain category in json"""
    items = session.query(
        Item).filter_by(id=category_id).one()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/api/categories.json')
def categoriesJSON():
    """Returns all categories in json"""
    categories = session.query(Category).all()
    return jsonify(Categories=[c.serialize for c in categories])


	
@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    user_session['access_token'] = access_token, ''
    return redirect(url_for('index'))
 
 
@google.tokengetter
def get_access_token():
    return user_session.get('access_token')
 
 
def main():
    app.debug = True
    app.secret_key = 'super_secret_key'
    app.run(host = '0.0.0.0', port = 5000)
 
 
if __name__ == '__main__':
    main()