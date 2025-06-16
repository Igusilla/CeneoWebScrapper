from flask import Flask

app = Flask(__name__)

from app import views_object

app.run(debug=True)