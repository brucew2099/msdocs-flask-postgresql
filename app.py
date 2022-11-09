'''
Imports
'''
from datetime import datetime
import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

from models import Restaurant, Review, setup_db

app = Flask(__name__, static_folder='static')
csrf = CSRFProtect(app)

# WEBSITE_HOSTNAME exists only in production environment
if 'WEBSITE_HOSTNAME' not in os.environ:
    # local development, where we'll use environment variables
    print("Loading config.development and environment variables from .env file.")
    app.config.from_object('azureproject.development')
else:
    # production
    print("Loading config.production.")
    app.config.from_object('azureproject.production')

app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

db = setup_db(app)

# Create databases, if databases exists doesn't issue create
# For schema changes, run "flask db migrate"
with app.app_context():
    db.create_all()
    db.session.commit()

@app.route('/', methods=['GET'])
def index():
    '''
    Returns the index page
    '''
    print('Request for index page received')
    restaurants = db.session.query(Restaurant).all()
    return render_template('index.html', restaurants=restaurants)

@app.route('/<int:restaurant_id>', methods=['GET'])
def details(restaurant_id):
    '''
    Returns a specific restaurant
    '''
    restaurant = Restaurant.query.where(Restaurant.id == restaurant_id).first()
    reviews = Review.query.where(Review.restaurant==restaurant_id)
    return render_template('details.html', restaurant=restaurant, reviews=reviews)

@app.route('/create', methods=['GET'])
def create_restaurant():
    '''
    Create a new Restaurant
    '''
    print('Request for add restaurant page received')
    return render_template('create_restaurant.html')

@app.route('/add', methods=['POST'])
@csrf.exempt
def add_restaurant():
    '''
    Add a new restaurant
    '''
    try:
        name = request.values.get('restaurant_name')
        street_address = request.values.get('street_address')
        description = request.values.get('description')
    except KeyError:
        # Redisplay the question voting form.
        return render_template('add_restaurant.html',
            error_message="You must include a restaurant name, address, and description",
        )
    else:
        restaurant = Restaurant()
        restaurant.name = name
        restaurant.street_address = street_address
        restaurant.description = description
        restaurant.add_restaurant_to_db()

        return redirect(url_for('details', restaurant_id=restaurant.id))

@app.route('/review/<int:restaurant_id>', methods=['POST'])
@csrf.exempt
def add_review(restaurant_id):
    '''
    Add a review to a restaurant
    '''
    try:
        user_name = request.values.get('user_name')
        rating = request.values.get('rating')
        review_text = request.values.get('review_text')
    except KeyError:
        #Redisplay the question voting form.
        return render_template('add_review.html',
            error_message="Error adding review"
        )
    else:
        review = Review()
        review.restaurant = restaurant_id
        review.review_date = datetime.now()
        review.user_name = user_name
        review.rating = int(rating)
        review.review_text = review_text
        review.add_review_to_db()

    return redirect(url_for('details', restaurant_id=restaurant_id))

@app.context_processor
def utility_processor():
    '''
    This is a processor that is called for every request.
    '''
    def star_rating(restaurant_id):
        reviews = Review.query.where(Review.restaurant==restaurant_id)

        ratings = []
        review_count = 0
        for review in reviews:
            ratings += [review.rating]
            review_count += 1

        avg_rating = sum(ratings)/len(ratings) if ratings else 0
        stars_percent = round((avg_rating / 5.0) * 100) if review_count > 0 else 0
        return {'avg_rating': avg_rating, 'review_count': review_count, \
            'stars_percent': stars_percent}

    return dict(star_rating=star_rating)

@app.route('/favicon.ico')
def favicon():
    '''
    Returns a favicon for the app.
    '''
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
   app.run()
