import datetime
import os
import requests

import firebase_admin
import pyrebase
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from firebase_admin import credentials, firestore

load_dotenv()

config = {
    'apiKey': os.environ['FIREBASE_API_KEY'],
    'authDomain': os.environ['FIREBASE_AUTH_DOMAIN'],
    "databaseURL": "xxxxxx",
    'storageBucket': os.environ['FIREBASE_STORAGE_BUCKET']
}
firebase = pyrebase.initialize_app(config)


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
    docs = db.collection('shnews').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1).stream()
    latestEntry = [doc.to_dict()['link'] for doc in docs]
    print(latestEntry)
    now = datetime.datetime.now()
    getTime = now.strftime('%H:%M:%S')
    news = requests.get('http://www.sakaehigashi.ed.jp/news/').content
    newsSoup = BeautifulSoup(news, 'html.parser')
    newsList = []
    newsEntryList = newsSoup.find_all(class_='entry')
    for newsEntry in newsEntryList:
        if newsEntry.find_all('a')[0].get('href') in latestEntry[0]:
            break
        else:
            newsData = {}
            title = newsEntry.find_all('h3')[0].text.replace("\u3000", " ")
            date = newsEntry.find_all(class_='date')[0].text
            gtime = newsEntry.find_all(class_='time')[0].text.strip("投稿時刻")
            postDateTime = date + gtime
            category = newsEntry.find_all(class_='cat')[0].find_all('a')[0].text
            body = newsEntry.text.replace(title, "").replace(date, "").replace(
                "カテゴリー："+category, "").replace("投稿時刻", "").replace(gtime, "").replace("\n", "")
            if len(body) > 100:
                body = body[0:100] + "..."
            link = newsEntry.find_all('a')[0].get('href')
            images = []
            for imageArea in newsEntry.find_all('img'):
                images.append(imageArea.get('src'))
            newsData = {
                "title": title,
                "postDateTime": postDateTime,
                "body": body,
                "link": link,
                "category": category,
                "images": images
            }
            newsList.append(newsData)

    sendNewsData = []
    for value in reversed(newsList):
        sendNewsData.append(value)
        db.collection('shnews').add({
            "title": value["title"],
            "postDateTime": value["postDateTime"],
            "link": value["link"],
            "category": value["category"],
            "images": value["images"],
            'timestamp': firestore.SERVER_TIMESTAMP
        })
    print(sendNewsData)
    returnData = {
        "newsData": sendNewsData,
        "getTime": getTime
    }
    return returnData


if __name__ == "__main__":
    main()
