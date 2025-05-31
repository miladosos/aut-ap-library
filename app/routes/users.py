from flask import jsonify, request
from app.application import app
import json

def sync(data_base):
    with open('/home/arian/main/code/chert-pert/aut-ap-library/db.json', 'w') as fp:
        json.dump(data_base, fp)

@app.route("/api/v1/users")
def get_users():
    with open('/home/arian/main/code/chert-pert/aut-ap-library/db.json') as fp:
        data_base = json.load(fp)
    return jsonify(data_base['users'])


@app.route("/api/v1/users/<user_id>")
def get_user(user_id: str):
    with open('/home/arian/main/code/chert-pert/aut-ap-library/db.json') as fp:
        data_base = json.load(fp)
    user = {}
    for i in data_base['users']:
        if str(i['id']) == user_id:
            user = i
            break
    return jsonify({"user": user})


@app.route("/api/v1/users", methods=["POST"])
def create_user():
    with open('/home/arian/main/code/chert-pert/aut-ap-library/db.json') as fp:
        data_base = json.load(fp)
    user = json.loads(request.data.decode())
    user['id'] = str(int(data_base['users'][-1]['id'])+1)
    user['reserved_books'] = []
    data_base['users'].append(user)
    sync(data_base)
    return jsonify({"user": user})


@app.route("/api/v1/users/<user_id>", methods=["PUT"])
def update_user(user_id: str):
    with open('/home/arian/main/code/chert-pert/aut-ap-library/db.json') as fp:
        data_base = json.load(fp)
    user = {}
    for i in data_base['users']:
        if str(i['id']) == user_id:
            user = i
            break
    update_user = json.loads(request.data.decode())
    user['username'] = update_user['username']
    user['name'] = update_user['name']
    user['email'] = update_user['email']
    sync(data_base)
    return jsonify({"user": {}})
