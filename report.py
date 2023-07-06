import argparse
from pymongo import MongoClient
import html_generator as html_gen
import os
import shutil
from bson.objectid import ObjectId


parser = argparse.ArgumentParser()

parser.add_argument("-d", "--database", help="database to generate report")
parser.add_argument("-c", "--collection", help="collection to generate report")
parser.add_argument("-u", "--uri", help="Connection string")
parser.add_argument("-l", "--limit", default = 20, help="number of entries for each topic")
parser.add_argument("-f", "--folder", default = "report", help="folder name with index.html")



indexes_to_create = ["attr.docsExamined", "attr.keysExamined", "attr.durationMillis", "attr.planSummary","attr.queryHash"]

args = parser.parse_args()
hashes = []

if (args.database is None):
    print ("Qual database?")
    exit(0)

if (args.collection is None):
    print ("Qual collection?")
    exit(0)

current_path = os.path.abspath(os.getcwd())
destination_folder = current_path + "/" + args.folder

print("deleting destination folder and re-creating...")
shutil.rmtree(destination_folder, ignore_errors=True)
os.makedirs(destination_folder)

print("Connecting to MongoDB")

try:
    client = MongoClient(args.uri)
    db = client[args.database]
    collection = args.collection
    db["collection"].find_one()
    print("Connected to the database")
except Exception as e:
    print("Error connecting to the database" + str(e))
    exit(1)

for i in indexes_to_create:
    try:
        db[collection].create_index(i)
    except:
        print("Index " + i + " already exists")

pipeline = [
{"$match" :    {"attr.planSummary" : 'COLLSCAN', "attr.queryHash" : {"$exists": True }}},
{"$project" : {"attr.ns" : 1, "attr.queryHash" : 1}},
{"$group" :   {"_id" : { "ns" : "$attr.ns", "hash" : "$attr.queryHash"},"total" : {"$sum" : 1}}},
{"$sort" : {"total" : -1}},
{"$limit" : int(args.limit)}
]

result = db[collection].aggregate(pipeline)

mytable = []

for i in result:
    myobj = {}
    myobj["ns"] = i["_id"]["ns"]
    myobj["total"] = i["total"]
    myobj["hash"] = '<a href="' + str(i["_id"]["hash"]) + '.html"' +'>' + i["_id"]["hash"] +'</a>'
    try:
        exists = hashes.index(i["_id"]["hash"])
    except:
        exists = -1
    if exists == -1:
        hashes.append(i["_id"]["hash"])

    mytable.append(myobj)

header = ["namespace (database.collection)", "Total", "queryHash"]

collscan = html_gen.html_generate_table(header, mytable, "Collection Scan")

# -- slow query:

projection = {"attr.durationMillis" : 1, "attr.ns" : 1, "attr.queryHash": 1 }
result = db[collection].find({}, projection).sort("attr.durationMillis", -1).limit(int(args.limit))

mytable = []


for i in result:
    myobj = {}
    if 'attr' in i and 'ns' in i['attr']:
      myobj["ns"] = i["attr"]["ns"]
    else:
      myobj["ns"] = ""
    myobj["durationMillis"] = str(i["attr"]["durationMillis"]) + "  (" + str(round(i["attr"]["durationMillis"]/1000,0)) + " seconds)"
    myobj["hash"] = str(i["_id"])
    if 'queryHash' in i["attr"]:
        myobj["hash"] = '<a href="' + str(i["attr"]["queryHash"]) + '.html"' +'>' + i["attr"]["queryHash"] +'</a>'
        try:
            exists = hashes.index(i["attr"]["queryHash"])
        except:
            exists = -1
        if exists == -1:
            hashes.append(i["attr"]["queryHash"])

    if len(myobj["hash"]) == 24:
        myobj["hash"] = '<a href="' + str(i["_id"]) + '.html"' +'>' + str(i["_id"]) +'</a>'
        try:
            exists = hashes.index(str(i["_id"]))
        except:
            exists = -1
        if exists == -1:
            hashes.append(str(i["_id"]))

    mytable.append(myobj)

header = ["namespace (database.collection)", "Time (milisseconds)", "queryHash/_id"]

slowqueries = html_gen.html_generate_table(header, mytable, "Slow Queries")

# Docs Examined:

projection = {"attr.docsExamined" : 1, "attr.ns" : 1, "attr.queryHash": 1 }
result = db[collection].find({}, projection).sort("attr.docsExamined", -1).limit(int(args.limit) * 2)

mytable = []


for i in result:
    myobj = {}
    myobj["ns"] = i["attr"]["ns"]
    myobj["durationMillis"] = i["attr"]["docsExamined"]
    myobj["hash"] = str(i["_id"])

    if len(myobj["hash"]) == 24:
        myobj["hash"] = '<a href="' + str(i["_id"]) + '.html"' +'>' + str(i["_id"]) +'</a>'
        try:
            exists = hashes.index(str(i["_id"]))
        except:
            exists = -1
        if exists == -1:
            hashes.append(str(i["_id"]))

    mytable.append(myobj)

header = ["namespace (database.collection)", "docsExamined", "Query ID"]

docs_examined = html_gen.html_generate_table(header, mytable, "Top docs Examined")

# docs returned

projection = {"attr.nreturned" : 1, "attr.ns" : 1, "attr.queryHash": 1 }
result = db[collection].find({}, projection).sort("attr.nreturned", -1).limit(int(args.limit))

mytable = []


for i in result:
    myobj = {}
    myobj["ns"] = i["attr"]["ns"]
    myobj["durationMillis"] = i["attr"]["nreturned"]
    myobj["hash"] = str(i["_id"])
    if len(myobj["hash"]) == 24:
        myobj["hash"] = '<a href="' + str(i["_id"]) + '.html"' +'>' + str(i["_id"]) +'</a>'
        try:
            exists = hashes.index(str(i["_id"]))
        except:
            exists = -1
        if exists == -1:
            hashes.append(str(i["_id"]))

    mytable.append(myobj)

header = ["namespace (database.collection)", "Docs Returned", "Query ID"]

docs_returned = html_gen.html_generate_table(header, mytable, "Top documents returned")


print("Gerando relatorio")

html_gen.generate_main(collscan + slowqueries + docs_examined +
                             docs_returned,destination_folder)

for h in hashes:
    hash_details = db[collection].find_one({"attr.queryHash" : h})

    if hash_details is None:
        hash_details = db[collection].find_one({"_id" : ObjectId(h)})
    html_gen.generate_detail(hash_details,h,destination_folder)
