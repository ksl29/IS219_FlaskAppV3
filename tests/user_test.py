import logging

from app import db
from app.db.models import User, Song
from faker import Faker

def test_adding_user(application):
    log = logging.getLogger("myApp")
    with application.app_context():
        assert db.session.query(User).count() == 0
        #showing how to add a record
        #create a record
        user = User('keith@webizly.com', 'testtest',0)
        #add it to get ready to be committed
        db.session.add(user)
        #call the commit
        #db.session.commit()
        #assert that we now have a new user
        #assert db.session.query(User).count() == 1
        #finding one user record by email
        user = User.query.filter_by(email='keith@webizly.com').first()
        log.info(user)
        #asserting that the user retrieved is correct
        assert user.email == 'keith@webizly.com'
        
        #checking cascade delete
        db.session.delete(user)
        assert db.session.query(User).count() == 0




