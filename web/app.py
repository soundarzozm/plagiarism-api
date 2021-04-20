from flask import Flask, json, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import spacy

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")

db = client.SimilarityDB
users = db["Users"]

def UserExists(username):
    if users.find({"username": username}).count() == 0:
        return False
    else:
        return True    

class Register(Resource):
    def post(self):

        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]

        if UserExists(username):
            retJson = {
                "status": 301,
                "msg": "username unavailable"
            }
            return jsonify(retJson)

        hashed_pw = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())

        users.insert({
            "username": username,
            "password": hashed_pw,
            "tokens": 10
        })

        retJson = {
            "status": 200,
            "msg": "success"
        }

        return jsonify(retJson)        