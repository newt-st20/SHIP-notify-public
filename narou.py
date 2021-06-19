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
            'lastup': eachDoc['lastup'],
            'channels': eachDoc['channels']
        })
    newData = []
    for eachData in data:
        response = requests.get(
                    'https://api.syosetu.com/novelapi/api/?out=json&ncode='+eachData['ncode']+'&of=t-gl-ga-e')
        responseJson = response.json()
        lastUpdate = responseJson[1]['general_lastup']
        count = responseJson[1]['general_all_no']
        end = responseJson[1]['end']
        if eachData['lastup'] != lastUpdate:
            db.collection('narou').document(eachData['ncode']).update({
                'count': count,
                'lastup': lastUpdate,
                'ended': end
            })
            newData.append({
                'ncode': eachData['ncode'],
                'title': eachData['title'],
                'count': count,
                'lastup': lastUpdate,
                'ended': end,
                'channels': eachData['channels']
            })
    return newData


def add(ncode, channel):
    if db.collection('narou').document(str(ncode)).get().exists:
        db.collection('narou').document(str(ncode)).update({
            'channels' : firestore.arrayUnion([str(channel)])
        })
    else:
        try:
            response = requests.get(
                'https://api.syosetu.com/novelapi/api/?out=json&ncode='+str(ncode)+'&of=t-gl-ga-e')
            responseJson = response.json()
            db.collection('narou').document(str(ncode)).set({
                'title': responseJson[1]['title'],
                'lastup': responseJson[1]['general_lastup'],
                'count': responseJson[1]['general_all_no'],
                'ended': responseJson[1]['end'],
                'channels': [str(channel)]
                })
        except Exception as e:
            return str(e)
    return "success"


def remove(ncode, channel):
    if db.collection('narou').document(str(ncode)).get().exists:
        try:
            db.collection('narou').document(str(ncode)).update({
                'channels' : firestore.arrayRemove([str(channel)])
            })
        except Exception as e:
            return str(e)
    else:
        return "error"
    return "success"


def list(channel):
    data = []
    docs = db.collection('narou').where('channels', 'array_contains', str(channel)).stream()
    for doc in docs:
        eachDoc = doc.to_dict()
        data.append({
            'ncode': doc.id,
            'title': eachDoc['title']
        })
    return data


if __name__ == "__main__":
    main()
