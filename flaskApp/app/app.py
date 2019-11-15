from flask import Flask, render_template, request, session, url_for, redirect
from dotenv import load_dotenv
from collections import OrderedDict 
import os


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# db config
# app.config['SQLALCHEMY_DATABASE_URI'] : 'sqlite:///'+os.path.join(basedir, 'data.sqlite')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)
