'''
Imports the
'''
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, validates
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# declarative base class
Base = declarative_base()
metadata = Base.metadata

# Initialize the database connection
db = SQLAlchemy()

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate()

def setup_db(app):
    '''
    Setup the database
    '''
    db.app = app
    db.init_app(app)
    migrate.init_app(app, db)
    return db

session = db.session

class Restaurant(db.Model):
    '''
    This is the base class for all restaurants
    '''
    __tablename__ = 'restaurant'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    street_address = Column(String(50))
    description = Column(String(250))

    def __str__(self):
        return self.name

    def add_restaurant_to_db(self):
        session.add(self)
        session.commit()

class Review(db.Model):
    '''
    A review for a restaurant
    '''
    __tablename__ = 'review'
    id = Column(Integer, primary_key=True)
    restaurant = Column(Integer, ForeignKey('restaurant.id', ondelete="CASCADE"))
    user_name = Column(String(30))
    rating = Column(Integer)
    review_text = Column(String(500))
    review_date = Column(DateTime)

    @validates('rating')
    def validate_rating(self, key, value):
        '''
        Rating must be a number between 1 and 5
        '''
        assert value is None or (1 <= value <= 5)
        return value

    def __str__(self):
        return f'{self.restaurant.name} ( {self.review_date.strftime("%x")} )'

    def add_review_to_db(self):
        db.session.add(self)
        db.session.commit()
