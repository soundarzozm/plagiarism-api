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
    if users.find({"username": username}).count() >= 1:
        return True
    return False

def VerifyPassword(username, password):
    if not UserExists(username):
        return False

    hashed_pw = users.find({
        "username": username
    })[0]["password"]

    return bcrypt.checkpw(password.encode("utf8"), hashed_pw)

def CountTokens(username):
    num_tokens = users.find({
        "username": username
    })[0]["tokens"]

    return num_tokens

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

class Detect(Resource):
    def post(self):

        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]
        text1 = postedData["text1"]
        text2 = postedData["text2"]

        if UserExists(username) == False:
            retJson = {
                "status": 301,
                "msg": "username not found"
            }
            return jsonify(retJson)

        if VerifyPassword(username, password) == False:
            retJson = {
                "status": 302,
                "msg": "incorrect password"
            }
            return jsonify(retJson)

        num_tokens = CountTokens(username)

        if num_tokens < 1:
            retJson = {
                "status": 303,
                "msg": "tokens exhausted"
            }
            return jsonify(retJson)

        model = spacy.load("en_core_web_sm")

        text1 = model(text1)
        text2 = model(text2)

        ratio = text1.similarity(text2)

        retJson = {
            "status": 200,
            "similarity": ratio,
            "msg": "similarity score calculated"
        }

        users.update({
            "username": username
        },{
            "$set":{
                "tokens": num_tokens - 1
            }
        })

        return jsonify(retJson)

class Refill(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        adminPw = postedData["adminPw"]
        refillAmt = postedData["refill"]

        if UserExists(username) == False:
            retJson = {
                "status": 301,
                "msg": "username not found"
            }
            return jsonify(retJson)

        correct_pw = "abc123"

        if adminPw != correct_pw:
            retJson = {
                "status": 304,
                "msg": "invalid admin password"
            }    
            return jsonify(retJson)

        num_tokens = CountTokens(username)

        users.update({
            "username": username
        },{
            "$set":{
                "tokens": num_tokens + refillAmt
            }
        })

        retJson = {
            "status": 200,
            "msg": "success"
        }

        return jsonify(retJson)

api.add_resource(Register, "/register")
api.add_resource(Detect, "/detect")
api.add_resource(Refill, "/refill")

if __name__ == "__main__":
    app.run(host="0.0.0.0")