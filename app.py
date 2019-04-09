import os

import pandas as pd
import numpy as np
import pymongo

from flask import Flask, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from bson.son import SON


app = Flask(__name__)


#################################################
# Database Setup
#################################################

#Making Mongo DB connections
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)

#Creating DB
db = client.craigslist_db

#Creating collections for the DB
craigslist_collection = db.craigs.find()


@app.route("/")
def index():
    """Return the homepage."""
    return render_template("index.html")
#=========================
@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('static/css', path)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)

	
	
#======================	


@app.route("/alldata")
def maps():
	lista = []

	rent_list = db.craigslist_collection.find()
#list(rent_list)

	for i in list(rent_list):
		dic = {}
		for j,k in i.items():
			if not j == "_id":
				dic[j] = k
		lista.append(dic)
	return jsonify(lista)    
	
@app.route("/names")
def names():
    """Return a list of sample names."""


    return jsonify(db.craigslist_collection.distinct('City'))


@app.route("/region")
def regions():
    """Return a list of sample names."""


    return jsonify(db.craigslist_collection.distinct('Region'))



@app.route("/regioncount")
def samples():
    
    """Return `otu_ids`, `otu_labels`,and `sample_values`."""
    query = [{"$unwind": "$City"},
                {"$group": {"_id": "$City", "count": {"$sum": 1}}}, 
                {"$sort": SON([("count", -1), ("_id", -1)])}]
    labels = []
    values = []
    for data in list(db.craigslist_collection.aggregate(query))[:10]:
        
        labels.append(data["_id"])
        values.append(data["count"])
    trace = {"labels": labels, "values": values}
    return jsonify(trace)


@app.route("/cityavgprice")
def sample():
    
    """Return `otu_ids`, `otu_labels`,and `sample_values`."""
    query = [{"$group": {"_id":"$City","avg_price": {"$avg": "$price"}}},
         {"$sort": SON([("count", -1), ("avg_price", -1)])}]
    
    labels = []
    values = []
    
    for data in list(db.craigslist_collection.aggregate(query))[1:11]:
        
        labels.append(data["_id"])
        values.append(int(data["avg_price"]))
    trace = {"labels": labels, "values": values}
    
    return jsonify(trace)

   
@app.route("/metadata/<sample>")
def sample_metadata(sample):
    dic = {}
    
    max_p = [{"$match" : {"City":sample}},
             {"$group" : {"_id": "$City","max_rent" : {"$max" : "$price"}}}]

    max_price = list(db.craigslist_collection.aggregate(max_p))

    min_p = [{"$match" : {"City":sample}},
             {"$group" : {"_id": "$City","max_rent" : {"$min" : "$price"}}}]

    min_price = list(db.craigslist_collection.aggregate(min_p))

    dic["Max Price"] = max_price[0]["max_rent"]
    dic["Min Price"] = max_price[0]["max_rent"]
    return jsonify(dic)


if __name__ == "__main__":
    app.run()
