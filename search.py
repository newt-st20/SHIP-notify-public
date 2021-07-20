import os
import json

from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

load_dotenv()

if not firebase_admin._apps:
    CREDENTIALS = credentials.Certificate({
    'type': 'service_account',
    'token_uri': 'https://oauth2.googleapis.com/token',
    'project_id': os.environ['FIREBASE_PROJECT_ID'],
    'client_email': os.environ['FIREBASE_CLIENT_EMAIL'],
    'private_key': os.environ['FIREBASE_PRIVATE_KEY'].replace('\\n', '\n')
    })
    firebase_admin.initialize_app(CREDENTIALS,{'databaseURL': 'https://'+os.environ['FIREBASE_PROJECT_ID']+'.firebaseio.com'})
db = firestore.client()


def file(id):
    data = []
    docs = db.collection('shipPost').where('id', '==', int(id)).stream()
    for doc in docs:
        eachDoc = doc.to_dict()
        data.append([eachDoc['title'], eachDoc['link'], eachDoc['date']])
    return data


def info(id):
    data = []
    item = json.load(open('json/ship.json', 'r', encoding="utf-8_sig"))
    docs = db.collection('shipPost').where('id', '==', int(id)).stream()
    for doc in docs:
        eachDoc = doc.to_dict()
        if "high" in eachDoc["channel"]:
            data.append([eachDoc['title'], eachDoc['date'], eachDoc['folder'], eachDoc['link'], item["pageList"][item["pagePosition"].index(eachDoc["channel"])]["name"], doc.id])
        else:
            data.append([eachDoc['title'], eachDoc['date'], eachDoc['folder'], "", item["pageList"][item["pagePosition"].index(eachDoc["channel"])]["name"], doc.id])
    print(data)
    return data


def recently(type, howmany):
    itemNameList = json.load(open('json/ship.json', 'r', encoding="utf-8_sig"))["pageList"]
    data = []
    docs = db.collection("shipPost").where('channel', '==', itemNameList[type]["collectionName"]).order_by('id', direction=firestore.Query.DESCENDING).limit(int(howmany)).stream()
    for doc in docs:
        eachDoc = doc.to_dict()
        data.append({
            "title":  eachDoc['title'],
            "date": eachDoc['date'],
            "id": eachDoc['id']
        })
    return data


def count(type):
    itemNameList = json.load(open('json/ship.json', 'r', encoding="utf-8_sig"))["pageList"]
    dbc = db.collection('count')
    try:
        docDict = dbc.document(itemNameList[type]["collectionName"]).get().to_dict()
        return docDict['count']
    except Exception as e:
        return 0


if __name__ == "__main__":
    info(32562)
