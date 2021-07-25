import copy
import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

LINE_BETA_CHANNEL_ACCESS_TOKEN = os.environ["LINE_BETA_CHANNEL_ACCESS_TOKEN"]


def main(data):
    getTime = str(data['getTime'])
    jsonOpen = open('json/push.json', 'r', encoding="utf-8_sig")
    jsonLoad = json.load(jsonOpen)
    jsonData = jsonLoad['flexMessage']
    jsonData['messages'][0]['contents']['body']['contents'][2]['text'] = "getTime: " + getTime
    separate = jsonLoad["separate"]
    highConData = data['highCon']
    if len(highConData) != 0:
        message1 = {
            "type": "box",
            "layout": "vertical",
            "margin": "xxl",
            "spacing": "sm",
            "contents": [{
                    "type": "text",
                    "text": "高校連絡事項",
                    "size": "xl",
                    "color": "#1DB446",
                }
            ]
        }
        for a in highConData:
            message1['contents'].append(separate)
            jsonEachMenuDate = copy.deepcopy(jsonLoad["eachMenuDate"])
            jsonEachMenuDate["contents"][1]["text"] = a["date"]
            message1['contents'].append(jsonEachMenuDate)
            jsonEachMenuFolder = copy.deepcopy(jsonLoad["eachMenuFolder"])
            jsonEachMenuFolder["contents"][1]["text"] = a["folder"] if a["folder"]!="" else "root"
            message1['contents'].append(jsonEachMenuFolder)
            jsonEachMenuTitle = copy.deepcopy(jsonLoad["eachMenuTitle"])
            jsonEachMenuTitle["contents"][1]["text"] = a["title"]
            message1['contents'].append(jsonEachMenuTitle)
            jsonEachMenuDescription = copy.deepcopy(jsonLoad["eachMenuDescription"])
            jsonEachMenuDescription["contents"][1]["text"] = a["description"]
            message1['contents'].append(jsonEachMenuDescription)
        jsonData['messages'][0]['contents']['body']['contents'].append(message1)
    highStudyData = data['highStudy']
    if len(highStudyData) != 0:
        message2 = {
            "type": "box",
            "layout": "vertical",
            "margin": "xxl",
            "spacing": "sm",
            "contents": [{
                    "type": "text",
                    "text": "高校学習教材",
                    "size": "xl",
                    "color": "#1DB446",
                }
            ]
        }
        for a in highStudyData:
            message2['contents'].append(separate)
            jsonEachMenuDate = copy.deepcopy(jsonLoad["eachMenuDate"])
            jsonEachMenuDate["contents"][1]["text"] = a["date"]
            message2['contents'].append(jsonEachMenuDate)
            jsonEachMenuFolder = copy.deepcopy(jsonLoad["eachMenuFolder"])
            jsonEachMenuFolder["contents"][1]["text"] = a["folder"] if a["folder"]!="" else "root"
            message2['contents'].append(jsonEachMenuFolder)
            jsonEachMenuTitle = copy.deepcopy(jsonLoad["eachMenuTitle"])
            jsonEachMenuTitle["contents"][1]["text"] = a["title"]
            message2['contents'].append(jsonEachMenuTitle)
        jsonData['messages'][0]['contents']['body']['contents'].append(message2)

    betaheaders = {
        'Authorization': 'Bearer ' + LINE_BETA_CHANNEL_ACCESS_TOKEN,
        'Content-type': 'application/json'
    }

    broadcastEndPoint = "https://api.line.me/v2/bot/message/broadcast"
    print(jsonData)
    if len(highConData) != 0 or len(highStudyData) != 0:
        response = requests.post(broadcastEndPoint, json=jsonData, headers=betaheaders)
        if response.status_code != 200:
            logMessage = "Something error happend on LINE. \n\n[error message]\n"+ response.text +"\n\n[post json data]\n" + jsonData
        else:
            logMessage = "Send message succeed on LINE.\n[post json data]\n" + jsonData
        return logMessage


if __name__ == "__main__":
    main()