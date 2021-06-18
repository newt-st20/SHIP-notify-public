import os
import requests

import psycopg2
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

load_dotenv()

DATABASE_URL = os.environ['DATABASE_URL']

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


def add(ncode):
    if 'ncode' in ncode:
        return ["error", "第2引数にはURLの末尾にある小説のncodeを入れてください。"]
    response = requests.get(
        'https://api.syosetu.com/novelapi/api/?out=json&ncode='+ncode+'&of=t-gl-ga-e')
    try:
        responseJson = response.json()
        title = responseJson[1]['title']
        lastUpdate = responseJson[1]['general_lastup']
        count = responseJson[1]['general_all_no']
        end = responseJson[1]['end']
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT ncode, lastup, count, title FROM narou')
                result = cur.fetchall()
                if len(result) != 0:
                    return ["error", "この小説はすでに更新通知リストに追加されています。"]
                cur.execute('INSERT INTO narou (title, ncode, lastup, count, ended) VALUES (%s, %s, %s, %s, %s)', [
                    title, ncode, lastUpdate, count, end])
            conn.commit()
    except Exception as e:
        print(str(e))
        return ["error", str(e)]
    return ["success", title, "https://ncode.syosetu.com/"+ncode]


def remove(ncode):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT ncode, lastup, count, title FROM narou')
                result = cur.fetchall()
                if len(result) != 0:
                    try:
                        cur.execute(
                            'DELETE FROM narou WHERE ncode = %s', [ncode])
                    except Exception as e:
                        return str(e)
            conn.commit()
    except Exception as e:
        print(str(e))
        return ["error", str(e)]
    return ["success", "https://ncode.syosetu.com/"+ncode]


def list():
    data = []
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT ncode, title FROM narou WHERE ended = 1')
            result = cur.fetchall()
            for item in result:
                data.append([item[0], item[1]])
        conn.commit()
    return data


def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')


if __name__ == "__main__":
    main()
