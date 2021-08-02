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


def main():
    itemNameList = json.load(open('json/ship.json', 'r', encoding="utf-8_sig"))["pagePosition"]
    for channel in itemNameList:
        docs = db.collection('shipPost').where('channel', '==', channel).get()
        count = len(docs)
        print(channel, count)
        db.collection('count').document(channel).update({'count': count, 'update': firestore.SERVER_TIMESTAMP})


if __name__ == "__main__":
    main()