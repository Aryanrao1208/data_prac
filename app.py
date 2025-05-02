### File: app.py
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Configuration
app.config["MONGO_URI"] = "mongodb://mongo:27017/generaldb"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@mysql/generaldb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database Clients
mongo = PyMongo(app)
db = SQLAlchemy(app)

# Example SQL model (for MySQL)
class LogEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    collection = db.Column(db.String(64))
    operation = db.Column(db.String(32))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/data/<collection>', methods=['POST'])
def create_data(collection):
    data = request.json
    inserted = mongo.db[collection].insert_one(data)
    log = LogEntry(collection=collection, operation="CREATE")
    db.session.add(log)
    db.session.commit()
    return jsonify({"id": str(inserted.inserted_id)}), 201

@app.route('/data/<collection>/<id>', methods=['GET'])
def get_data(collection, id):
    from bson.objectid import ObjectId
    doc = mongo.db[collection].find_one({"_id": ObjectId(id)})
    if not doc:
        return jsonify({"error": "Not found"}), 404
    doc['_id'] = str(doc['_id'])
    return jsonify(doc)

@app.route('/data/<collection>', methods=['GET'])
def list_data(collection):
    docs = mongo.db[collection].find()
    result = []
    for doc in docs:
        doc['_id'] = str(doc['_id'])
        result.append(doc)
    return jsonify(result)

@app.route('/data/<collection>/<id>', methods=['PUT'])
def update_data(collection, id):
    from bson.objectid import ObjectId
    update = request.json
    result = mongo.db[collection].update_one({"_id": ObjectId(id)}, {"$set": update})
    if result.matched_count == 0:
        return jsonify({"error": "Not found"}), 404
    log = LogEntry(collection=collection, operation="UPDATE")
    db.session.add(log)
    db.session.commit()
    return jsonify({"updated": True})

@app.route('/data/<collection>/<id>', methods=['DELETE'])
def delete_data(collection, id):
    from bson.objectid import ObjectId
    result = mongo.db[collection].delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Not found"}), 404
    log = LogEntry(collection=collection, operation="DELETE")
    db.session.add(log)
    db.session.commit()
    return jsonify({"deleted": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
