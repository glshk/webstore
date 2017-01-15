from flask import Flask

app = Flask('webstore', instance_relative_config=True)

app.config.from_object('config')
app.config.from_pyfile('config.py')

from webstore import models, views
from webstore.views import *

@app.route('/')
def index():
    return 'Hello World!'