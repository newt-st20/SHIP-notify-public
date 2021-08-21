import json
import os

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials, firestore

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

class Search:
    data = []
    item = json.load(open('json/ship.json', 'r', encoding="utf-8_sig"))
    def file(self, id):
        docs = db.collection('shipPost').where('id', '==', int(id)).stream()
        for doc in docs:
            eachDoc = doc.to_dict()
            self.data.append([eachDoc['title'], eachDoc['link'], eachDoc['date']])
        return self.data

    def info(self, id):
        docs = db.collection('shipPost').where('id', '==', int(id)).stream()
        for doc in docs:
            eachDoc = doc.to_dict()
            if "high" in eachDoc["channel"]:
                self.data.append([eachDoc['title'], eachDoc['date'], eachDoc['folder'], eachDoc['link'], self.item["pageList"][self.item["pagePosition"].index(eachDoc["channel"])]["name"], doc.id])
            else:
                self.data.append([eachDoc['title'], eachDoc['date'], eachDoc['folder'], "", self.item["pageList"][self.item["pagePosition"].index(eachDoc["channel"])]["name"], doc.id])
        return self.data

    def recently(self, type, howmany):
        itemNameList = self.item["pageList"]
        docs = db.collection("shipPost").where('channel', '==', itemNameList[type]["collectionName"]).order_by('id', direction=firestore.Query.DESCENDING).limit(int(howmany)).stream()
        for doc in docs:
            eachDoc = doc.to_dict()
            self.data.append({
                "title":  eachDoc['title'],
                "date": eachDoc['date'],
                "id": eachDoc['id']
            })
        return self.data

    def count(self, type):
        itemNameList = self.item["pageList"]
        dbc = db.collection('count')
        try:
            docDict = dbc.document(itemNameList[type]["collectionName"]).get().to_dict()
            return docDict['count']
        except:
            return 0


if __name__ == "__main__":
    print(Search().file(8823))
