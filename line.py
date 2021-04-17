import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

if os.environ['STATUS'] == "remote":
    YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
    YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
    LINE_SUB_CHANNNEL_ACCESS_TOKEN = os.environ["LINE_SUB_CHANNNEL_ACCESS_TOKEN"]
else:
    YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_DEV_CHANNEL_ACCESS_TOKEN"]
    YOUR_CHANNEL_SECRET = os.environ["YOUR_DEV_CHANNEL_SECRET"]


def main(data):
    HighConData = data[2]
    HighStudyData = data[3]
    getTime = str(data[4])
    message1 = ""
    try:
        for a in HighConData:
            message1 += "\n・連絡事項:" + \
                a[1] + "-" + a[2] + "-" + \
                a[3].replace("\n", "")
            if a[4].replace("\n", "") != "":
                message1 += "\n《" + a[4].replace("\n", "") + "》"
    except Exception as e:
        message1 = "\n・連絡事項取得エラー:更新の有無を取得できませんでした"
        return str(e)
    message2 = ""
    try:
        for a in HighStudyData:
            message2 += "\n・学習教材:" + \
                a[1] + "-" + a[2] + "-" + \
                a[3].replace("\n", "")
    except Exception as e:
        message2 = "\n・学習教材取得エラー:更新の有無を取得できませんでした"
        return str(e)

    headers = {
        'Authorization': 'Bearer ' + YOUR_CHANNEL_ACCESS_TOKEN,
        'Content-type': 'application/json'
    }
    subheaders = {
        'Authorization': 'Bearer ' + LINE_SUB_CHANNNEL_ACCESS_TOKEN,
        'Content-type': 'application/json'
    }
    jsonOpen = open('json/push.json', 'r', encoding="utf-8_sig")
    jsonLoad = json.load(jsonOpen)
    mail = "【" + getTime.replace("-", "/") + "】\n" + message1 + message2
    broadcastEndPoint = "https://api.line.me/v2/bot/message/broadcast"
    jsonData = jsonLoad['default']
    jsonData['messages'][0]['text'] = mail
    print(jsonData)
    if message1 != "" or message2 != "":
        requests.post(broadcastEndPoint, json=jsonData, headers=headers)
        requests.post(broadcastEndPoint, json=jsonData, headers=subheaders)
        logMessage = "send message:" + \
            str(mail)+" send for all followed user."
        return logMessage


if __name__ == "__main__":
    main()
