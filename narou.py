import os
import requests

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

def main():
    data = []
    docs = db.collection('narou').stream()
    for doc in docs:
        eachDoc = doc.to_dict()
        data.append({
            'ncode': doc.id,
            'title': eachDoc['title'],
            'count': eachDoc['count'],
            'lastup': eachDoc['lastup']
        })
    newData = []
    for eachData in data:
        response = requests.get(
                    'https://api.syosetu.com/novelapi/api/?out=json&ncode='+eachData['ncode']+'&of=t-gl-ga-e')
        responseJson = response.json()
        if eachData['lastup'] != responseJson[1]['general_lastup']:
            db.collection('narou').document(eachData['ncode']).update({
                'count': responseJson[1]['general_all_no'],
                'lastup': responseJson[1]['general_lastup'],
                'ended': responseJson[1]['end']
            })
            newData.append({
                'ncode': eachData['ncode'],
                'title': eachData['title'],
                'count': responseJson[1]['general_all_no'],
                'lastup': responseJson[1]['general_lastup']
            })
    return newData


def add(ncode):
    try:
        doc = db.collection('narou').document(str(ncode)).get()
        if doc.exists:
            return "already"
        else:
            response = requests.get(
                'https://api.syosetu.com/novelapi/api/?out=json&ncode='+str(ncode)+'&of=t-gl-ga-e')
            responseJson = response.json()
            db.collection('narou').document(str(ncode)).set({
                'title': responseJson[1]['title'],
                'lastup': responseJson[1]['general_lastup'],
                'count': responseJson[1]['general_all_no'],
                'ended': responseJson[1]['end']
                })
            return "add"
    except Exception as e:
        return str(e)


def remove(ncode):
    try:
        doc = db.collection('narou').document(str(ncode)).get()
        if doc.exists:
            db.collection('narou').document(str(ncode)).delete()
            return "remove"
        else:
            return "error"
    except Exception as e:
        return str(e)


def list():
    data = []
    docs = db.collection('narou').stream()
    for doc in docs:
        eachDoc = doc.to_dict()
        data.append({
            'ncode': doc.id,
            'title': eachDoc['title']
        })
    return data


if __name__ == "__main__":
    main()
