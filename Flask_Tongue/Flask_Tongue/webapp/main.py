# main.py
from flask import Flask, render_template
from flask_restx import Api
from flask_cors import CORS
from todo import Todo

app = Flask(__name__)

api = Api(app, version='1,0', title='API 문서', description='Swagger 문서', doc="/api-docs")
api.add_namespace(Todo, '/Tongue_Project')

CORS(app)

@app.route('/')
def index():
    return "Hello Graph!"

@app.route('/frame')
def frame():
    return render_template('index.html')

