import copy
import json
import os
import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

LINE_BETA_CHANNEL_ACCESS_TOKEN = os.environ["LINE_BETA_CHANNEL_ACCESS_TOKEN"]


def main(data):
    now = datetime.datetime.now()
    date = now.strftime("%y%m%d")
    getTime = str(data['getTime'])
    jsonOpen = open('json/push.json', 'r', encoding="utf-8_sig")
    jsonLoad = json.load(jsonOpen)
    jsonData = jsonLoad['flexMessage']
    jsonData['messages'][0]['contents']['body']['contents'][2]['text'] = "getTime: " + getTime
    separate = jsonLoad["separate"]
    highConData = data['highCon']
    if len(highConData) != 0:
        highConMessage = copy.deepcopy(jsonLoad['channelHead'])
        highConMessage['contents'][0]['text'] = "高校連絡事項"
        for a in highConData:
            highConMessage['contents'].append(separate)
            jsonEachMenuDate = copy.deepcopy(jsonLoad["eachMenuDate"])
            jsonEachMenuDate["contents"][1]["text"] = a["date"]
            highConMessage['contents'].append(jsonEachMenuDate)
            jsonEachMenuFolder = copy.deepcopy(jsonLoad["eachMenuFolder"])
            jsonEachMenuFolder["contents"][1]["text"] = a["folder"] if a["folder"]!="" else "root"
            highConMessage['contents'].append(jsonEachMenuFolder)
            jsonEachMenuTitle = copy.deepcopy(jsonLoad["eachMenuTitle"])
            jsonEachMenuTitle["contents"][1]["text"] = a["title"]
            highConMessage['contents'].append(jsonEachMenuTitle)
            jsonEachMenuDescription = copy.deepcopy(jsonLoad["eachMenuDescription"])
            jsonEachMenuDescription["contents"][1]["text"] = a["description"]
            highConMessage['contents'].append(jsonEachMenuDescription)
        jsonData['messages'][0]['contents']['body']['contents'].append(highConMessage)
    highStudyData = data['highStudy']
    if len(highStudyData) != 0:
        highStudyMessage = copy.deepcopy(jsonLoad['channelHead'])
        highStudyMessage['contents'][0]['text'] = "高校学習教材"
        for a in highStudyData:
            highStudyMessage['contents'].append(separate)
            jsonEachMenuDate = copy.deepcopy(jsonLoad["eachMenuDate"])
            jsonEachMenuDate["contents"][1]["text"] = a["date"]
            highStudyMessage['contents'].append(jsonEachMenuDate)
            jsonEachMenuFolder = copy.deepcopy(jsonLoad["eachMenuFolder"])
            jsonEachMenuFolder["contents"][1]["text"] = a["folder"] if a["folder"]!="" else "root"
            highStudyMessage['contents'].append(jsonEachMenuFolder)
            jsonEachMenuTitle = copy.deepcopy(jsonLoad["eachMenuTitle"])
            jsonEachMenuTitle["contents"][1]["text"] = a["title"]
            highStudyMessage['contents'].append(jsonEachMenuTitle)
        jsonData['messages'][0]['contents']['body']['contents'].append(highStudyMessage)
    jsonData['messages'][0]['contents']['footer']['contents'][0]['action']['uri'] = "https://ship-assistant.web.app/log/"+data['logId']+"utm_source=line_"+date+"&utm_medium=LINE"

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
            logMessage = "Send message succeed on LINE.\n[post json data]\n" + str(jsonData)
        return logMessage


if __name__ == "__main__":
    main()