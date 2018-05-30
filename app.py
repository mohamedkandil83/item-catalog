from flask import Flask, redirect, url_for, jsonify, render_template, request
from flask import session as user_session
from flask_oauth import OAuth
from urllib2 import Request, urlopen, URLError
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Base, User, Category, Item
import json

# https://code.google.com/apis/console
GOOGLE_CLIENT_ID = '784859935364-03l0ofenuodrongl54fi6' \
    'kua606onf9e.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'lkOxBobk10_KeRH12R63JZCz'
# one of the Redirect URIs from Google APIs console
REDIRECT_URI = '/oauth2callback'

SECRET_KEY = 'development key'
DEBUG = True
app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()

# database connection
engine = create_engine(
    'sqlite:///final_catalog.db',
    connect_args={'check_same_thread': False}, echo=True)
Base.metadata.bind = engine
# session creation
DBSession = scoped_session(sessionmaker(bind=engine))
session = DBSession()
# print session

# followed the tutorial in
# https://pythonspot.com/login-to-flask-app-with-google/

google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts' +
                          '.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={
                              'scope':
                                  'https://www.googleapis' +
                                  '.com/auth/userinfo.email',
                              'response_type': 'code'},
                          access_token_url='https://accounts' +
                          '.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={
                              'grant_type': 'authorization_code'},
                          consumer_key=GOOGLE_CLIENT_ID,
                          consumer_secret=GOOGLE_CLIENT_SECRET)


@app.route('/')
def index():
    findAndCreateUser()
    categories = session.query(Category).all()
    c = session.query(Category).filter_by(id=1).one()
    # return render_template(
    # 'header.html',user_session=user_session,categories=categories, c=c)
    return redirect(url_for('showCategory', category_id=c.id))


@app.route('/items/add', methods=['POST'])
def editItem():
    # """Check if user is logged in"""
    # access_token = user_session.get('access_token')

    # authentication
    if user_session['user'] == -1:
        return redirect(url_for('login'))

    if request.form['item_id']:
        updatedItem = session.query(Item).filter_by(
            id=request.form['item_id']).one()
    else:
        updatedItem = Item()
    c = session.query(Category).filter_by(id=request.form['category_id']).one()
    u = session.query(User).filter_by(
        email=user_session['user']['email']).one()
    updatedItem.name = request.form['name']
    updatedItem.category = c
    updatedItem.description = request.form['description']
    updatedItem.picture = request.form['picture']

    # authorization
    if user.id != item.user_id:
        return redirect(url_for('login'))

    if request.method != 'POST':
        session.add(item)
        session.commit()
        return redirect(url_for('showCategory', category_id=c.id))
    else:
        return redirect(url_for('showCategory', category_id=c.id))


@app.route('/items/<int:item_id>/delete', methods=['GET'])
def deleteItem(item_id):
    # """Check if user is logged in"""
    # access_token = user_session.get('access_token')
    # authentication
    if user_session['user'] == -1:
        return redirect(url_for('login'))
    item = session.query(Item).filter_by(id=item_id).first()

    user = session.query(User).filter_by(
        email=user_session['user']['email']).first()

    # authorization
    if user.id != item.user_id:
        return redirect(url_for('login'))

    session.delete(item)
    session.commit()
    return redirect(url_for('showCategory', category_id=item.category_id))


@app.route('/showCategory')
def showCategory():
    findAndCreateUser()
    categories = session.query(Category).all()
    category_id = request.args.get('category_id')
    le_category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    if 'user' not in user_session:
        user_session['user'] = -1
    return render_template(
        'header.html',
        items=items,
        user_session=user_session, c=le_category,
        categories=categories
        )


@app.route('/login')
def login():
    access_token = user_session.get('access_token')
    if access_token is not None:
        return redirect(url_for('showCategory', category_id=1))
    callback = url_for('authorized', _external=True)
    return google.authorize(callback=callback)


@app.route('/logout')
def logout():
    user_session.clear()
    return redirect(url_for('showCategory', category_id=1))

# ===================
# JSON End Point
# ===================


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
        Item).filter_by(category_id=category_id).all()
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
    app.run(host='0.0.0.0', port=5000)

# helper


def findAndCreateUser():

    if 'access_token' in user_session:
        access_token = user_session.get('access_token')[0]
        headers = {'Authorization': 'OAuth '+access_token}
        req = Request(
            'https://www.googleapis.com/oauth2/v1/userinfo',
            None,
            headers
            )
        try:
            res = urlopen(req)
        except URLError, e:
            if e.code == 401:
                # Unauthorized - bad token
                user_session.pop('access_token', None)
                return redirect(url_for('login'))
            return res.read()

        user_session['user'] = json.load(res)
        # chek for an existing user
        user = session.query(User).filter_by(
            email=user_session['user']['email']).first()
        if user is None:
            newUser = User(
                name=user_session['user']['name'],
                email=user_session['user']['email'],
                picture=user_session['user']['picture']
                )
            session.add(newUser)
            session.commit()

if __name__ == '__main__':
    main()
