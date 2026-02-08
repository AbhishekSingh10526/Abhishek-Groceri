from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Config for Render (using environment variables)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db').replace('postgres://', 'postgresql://')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')

import models
import routes

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
