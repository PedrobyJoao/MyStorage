from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///storage.db'
app.config['SECRET_KEY'] = 'f1vcx8er3gfd89kllsa8854'
db = SQLAlchemy(app)

from app import routes