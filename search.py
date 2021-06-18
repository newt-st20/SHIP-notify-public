import os

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
    docs = db.collection('highCon').where('id', '==', int(id)).stream()
    for doc in docs:
        eachDoc = doc.to_dict()
        data.append([eachDoc['title'], eachDoc['link'], eachDoc['date']])
    docs = db.collection('highStudy').where('id', '==', int(id)).stream()
    for doc in docs:
        eachDoc = doc.to_dict()
        data.append([eachDoc['title'], eachDoc['link'], eachDoc['date']])
    docs = db.collection('highSchoolNews').where('id', '==', int(id)).stream()
    for doc in docs:
        eachDoc = doc.to_dict()
        data.append([eachDoc['title'], eachDoc['link'], eachDoc['date']])
    return data


def info(id):
    data = []
    docs = db.collection('highCon').where('id', '==', int(id)).stream()
    for doc in docs:
        eachDoc = doc.to_dict()
        data.append([eachDoc['title'], eachDoc['date'], eachDoc['folder'], eachDoc['link'], "高校連絡事項", doc.id])
    docs = db.collection('highStudy').where('id', '==', int(id)).stream()
    for doc in docs:
        eachDoc = doc.to_dict()
        data.append([eachDoc['title'], eachDoc['date'], eachDoc['folder'], eachDoc['link'], "高校学習教材", doc.id])
    docs = db.collection('highSchoolNews').where('id', '==', int(id)).stream()
    for doc in docs:
        eachDoc = doc.to_dict()
        data.append([eachDoc['title'], eachDoc['date'], eachDoc['folder'], eachDoc['link'], "高校学校通信", doc.id])
    docs = db.collection('juniorCon').where('id', '==', int(id)).stream()
    for doc in docs:
        eachDoc = doc.to_dict()
        data.append([eachDoc['title'], eachDoc['date'], eachDoc['folder'], "", "中学連絡事項", doc.id])
    docs = db.collection('juniorStudy').where('id', '==', int(id)).stream()
    for doc in docs:
        eachDoc = doc.to_dict()
        data.append([eachDoc['title'], eachDoc['date'], eachDoc['folder'], "", "中学学習教材", doc.id])
    docs = db.collection('juniorSchoolNews').where('id', '==', int(id)).stream()
    for doc in docs:
        eachDoc = doc.to_dict()
        data.append([eachDoc['title'], eachDoc['date'], eachDoc['folder'], "", "中学学校通信", doc.id])
    return data


def recently(type, howmany):
    data = []
    if type == 1:
        docs = db.collection('highCon').order_by('id', direction=firestore.Query.DESCENDING).limit(int(howmany)).stream()
        for doc in docs:
            eachDoc = doc.to_dict()
            data.append([eachDoc['title'], eachDoc['date'], eachDoc['id']])
    elif type == 2:
        docs = db.collection('highStudy').order_by('id', direction=firestore.Query.DESCENDING).limit(int(howmany)).stream()
        for doc in docs:
            eachDoc = doc.to_dict()
            data.append([eachDoc['title'], eachDoc['date'], eachDoc['id']])
    elif type == 3:
        docs = db.collection('juniorCon').order_by('id', direction=firestore.Query.DESCENDING).limit(int(howmany)).stream()
        for doc in docs:
            eachDoc = doc.to_dict()
            data.append([eachDoc['title'], eachDoc['date'], eachDoc['id']])
    elif type == 4:
        docs = db.collection('juniorStudy').order_by('id', direction=firestore.Query.DESCENDING).limit(int(howmany)).stream()
        for doc in docs:
            eachDoc = doc.to_dict()
            data.append([eachDoc['title'], eachDoc['date'], eachDoc['id']])
    elif type == 5:
        docs = db.collection('juniorSchoolNews').order_by('id', direction=firestore.Query.DESCENDING).limit(int(howmany)).stream()
        for doc in docs:
            eachDoc = doc.to_dict()
            data.append([eachDoc['title'], eachDoc['date'], eachDoc['id']])
    elif type == 6:
        docs = db.collection('highSchoolNews').order_by('id', direction=firestore.Query.DESCENDING).limit(int(howmany)).stream()
        for doc in docs:
            eachDoc = doc.to_dict()
            data.append([eachDoc['title'], eachDoc['date'], eachDoc['id']])
    return data


def count(type):
    data = []
    dbc = db.collection('count')
    if type == 1:
        docDict = dbc.document('highCon').get().to_dict()
        data = docDict['count']
    elif type == 2:
        docDict = dbc.document('highStudy').get().to_dict()
        data = docDict['count']
    elif type == 3:
        docDict = dbc.document('juniorCon').get().to_dict()
        data = docDict['count']
    elif type == 4:
        docDict = dbc.document('juniorStudy').get().to_dict()
        data = docDict['count']
    elif type == 5:
        docDict = dbc.document('juniorSchoolNews').get().to_dict()
        data = docDict['count']
    elif type == 6:
        docDict = dbc.document('highSchoolNews').get().to_dict()
        data = docDict['count']
    else:
        data = 0
    return data


if __name__ == "__main__":
    recently(5, 10)
