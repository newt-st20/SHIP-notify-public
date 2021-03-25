from linebot.models import TextSendMessage
from linebot import LineBotApi
import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

if os.environ['STATUS'] == "remote":
    YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
    YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
else:
    YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_DEV_CHANNEL_ACCESS_TOKEN"]
    YOUR_CHANNEL_SECRET = os.environ["YOUR_DEV_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)


def main(data):
    HighConData = data[2]
    HighStudyData = data[3]
    getTime = data[4]
    message1 = ""
    try:
        for a in HighConData:
            message1 += "\n・連絡事項:" + \
                a[1] + "-" + a[2] + "-" + \
                a[3].replace("\n", "")
            if a[4].replace("\n", "") != "":
                message1 += "\n《" + a[4].replace("\n", "") + "》"
    except:
        message1 = "\n・連絡事項取得エラー:更新の有無を取得できませんでした"
        import traceback
        traceback.print_exc()
    message2 = ""
    try:
        for a in HighStudyData:
            message2 += "\n・学習教材:" + \
                a[1] + "-" + a[2] + "-" + \
                a[3].replace("\n", "")
    except:
        message2 = "\n・学習教材取得エラー:更新の有無を取得できませんでした"
        import traceback
        traceback.print_exc()

    headers = {
        'Authorization': 'Bearer ' + YOUR_CHANNEL_ACCESS_TOKEN,
        'Content-type': 'application/json'
    }
    jsonOpen = open('json/push.json', 'r', encoding="utf-8_sig")
    jsonLoad = json.load(jsonOpen)
    mail = "【" + getTime.replace("-", "/") + "】\n" + message1 + message2
    broadcastEndPoint = "https://api.line.me/v2/bot/message/broadcast"
    jsonData = jsonLoad['default']
    jsonData['messages'][0]['text'] = mail
    print(jsonData)
    requests.post(broadcastEndPoint, json=jsonData, headers=headers)
    logMessage = "send message:" + \
        str(mail)+" send for all followed user."
    print(logMessage)


if __name__ == "__main__":
    main()
