import copy
import json
import os
import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_SUB_CHANNEL_ACCESS_TOKEN = os.environ["LINE_SUB_CHANNEL_ACCESS_TOKEN"]


def main(data):
    now = datetime.datetime.now()
    date = now.strftime("%y%m%d")
    getTime = str(data['getTime'])
    jsonOpen = open('json/push.json', 'r', encoding="utf-8_sig")
    jsonLoad = json.load(jsonOpen)
    jsonHead = jsonLoad['channelHead']
    jsonData = jsonLoad['flexMessage']
    eachMenu = jsonLoad['eachMenu']
    jsonData['messages'][0]['contents']['body']['contents'][2]['text'] = "getTime: " + getTime
    separate = jsonLoad["separate"]

    highConData = data['highCon']
    if len(highConData) != 0:
        highConMessage = copy.deepcopy(jsonHead)
        highConMessage['contents'][0]['text'] = "高校連絡事項"
        props = json.load(open('json/ship.json', 'r', encoding="utf-8_sig"))['pageList'][0]['lineProps']
        for a in highConData:
            highConMessage['contents'].append(separate)
            for prop in props:
                jsonEachMenu = copy.deepcopy(eachMenu)
                jsonEachMenu["contents"][0]["text"] = prop
                jsonEachMenu["contents"][1]["text"] = a[prop] if a[prop]!="" else "(empty)"
                highConMessage['contents'].append(jsonEachMenu)
        jsonData['messages'][0]['contents']['body']['contents'].append(highConMessage)
    
    highStudyData = data['highStudy']
    if len(highStudyData) != 0:
        highStudyMessage = copy.deepcopy(jsonHead)
        highStudyMessage['contents'][0]['text'] = "高校学習教材"
        props = json.load(open('json/ship.json', 'r', encoding="utf-8_sig"))['pageList'][1]['lineProps']
        for a in highStudyData:
            highStudyMessage['contents'].append(separate)
            for prop in props:
                jsonEachMenu = copy.deepcopy(eachMenu)
                jsonEachMenu["contents"][0]["text"] = prop
                jsonEachMenu["contents"][1]["text"] = a[prop] if a[prop]!="" else "(empty)"
                highStudyMessage['contents'].append(jsonEachMenu)
        jsonData['messages'][0]['contents']['body']['contents'].append(highStudyMessage)

    highSchoolNewsData = data['highSchoolNews']
    if len(highSchoolNewsData) != 0:
        highSchoolNewsMessage = copy.deepcopy(jsonHead)
        highSchoolNewsMessage['contents'][0]['text'] = "高校学校通信"
        props = json.load(open('json/ship.json', 'r', encoding="utf-8_sig"))['pageList'][2]['lineProps']
        for a in highSchoolNewsData:
            highSchoolNewsMessage['contents'].append(separate)
            for prop in props:
                jsonEachMenu = copy.deepcopy(eachMenu)
                jsonEachMenu["contents"][0]["text"] = prop
                jsonEachMenu["contents"][1]["text"] = a[prop] if a[prop]!="" else "(empty)"
                highSchoolNewsMessage['contents'].append(jsonEachMenu)
        jsonData['messages'][0]['contents']['body']['contents'].append(highSchoolNewsMessage)

    jsonData['messages'][0]['contents']['footer']['contents'][0]['action']['uri'] = "https://ship-assistant.web.app/log/"+data['logId']+"?utm_source=line_"+date+"&utm_medium=LINE"

    headers = {
        'Authorization': 'Bearer ' + LINE_CHANNEL_ACCESS_TOKEN,
        'Content-type': 'application/json'
    }
    subheaders = {
        'Authorization': 'Bearer ' + LINE_SUB_CHANNEL_ACCESS_TOKEN,
        'Content-type': 'application/json'
    }

    broadcastEndPoint = "https://api.line.me/v2/bot/message/broadcast"
    print(jsonData)
    if len(highConData) != 0 or len(highStudyData) != 0:
        response = requests.post(broadcastEndPoint, json=jsonData, headers=headers)
        subresponse = requests.post(broadcastEndPoint, json=jsonData, headers=subheaders)
        logMessage = ""
        if response.status_code != 200:
            logMessage += "Something error happend on LINE main. \n\n[error message]\n"+ response.text
        else:
            logMessage += "Send message succeed on LINE main."
        if subresponse.status_code != 200:
            logMessage += "Something error happend on LINE sub. \n\n[error message]\n"+ subresponse.text
        else:
            logMessage += "Send message succeed on LINE sub."
        return logMessage


if __name__ == "__main__":
    main()