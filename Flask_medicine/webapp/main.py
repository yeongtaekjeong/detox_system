# main.py
from flask import Flask, render_template
from flask_restx import Api
from flask_cors import CORS
from todo3 import Todo3

app = Flask(__name__)

api = Api(app, version='1,0', title='API 문서', description='Swagger 문서', doc="/api-docs")
# api.add_namespace(Todo2, '/DataAnalyze_api')
api.add_namespace(Todo3, '/Medicine_api')

CORS(app)

@app.route('/')
def index():
    return "Hello Graph!"

@app.route('/frame')
def frame():
    return render_template('index.html')

