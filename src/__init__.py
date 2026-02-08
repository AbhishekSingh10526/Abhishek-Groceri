from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder='../templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db').replace('postgres://', 'postgresql://')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
    
    db.init_app(app)
    
    with app.app_context():
        from . import models, routes
        db.create_all()
        # create admin if admin does not exist
        admin = models.User.query.filter_by(username='admin').first()
        if not admin:
            admin = models.User(username='admin', password='admin', name='admin', is_admin=True)
            db.session.add(admin)
            db.session.commit()
            
    return app
