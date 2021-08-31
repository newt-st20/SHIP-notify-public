import copy
import json
import os
import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_SUB_CHANNEL_ACCESS_TOKEN = os.environ["LINE_SUB_CHANNEL_ACCESS_TOKEN"]
LINE_BETA_CHANNEL_ACCESS_TOKEN = os.environ["LINE_BETA_CHANNEL_ACCESS_TOKEN"]


def main(data):
    date = datetime.datetime.now().strftime("%y%m%d")
    getTime = str(data['getTime'])
    jsonOpen = open('json/push.json', 'r', encoding="utf-8_sig")
    jsonLoad = json.load(jsonOpen)
    jsonHead = jsonLoad['channelHead']
    jsonData = jsonLoad['flexMessage']
    eachMenu = jsonLoad['eachMenu']
    jsonData['messages'][0]['contents']['body']['contents'][2]['text'] = "getTime: " + getTime
    separate = jsonLoad["separate"]
    channelList = jsonLoad['channelList']

    flag = False
    for index, channel in enumerate(channelList):
        channelData = data[channel['name']]
        if len(channelData) != 0:
            flag = True
            message = copy.deepcopy(jsonHead)
            message['contents'][0]['text'] = channel['jpName']
            props = json.load(open('json/ship.json', 'r', encoding="utf-8_sig"))['pageList'][index]['lineProps']
            for a in channelData:
                message['contents'].append(separate)
                for prop in props:
                    jsonEachMenu = copy.deepcopy(eachMenu)
                    jsonEachMenu["contents"][0]["text"] = prop
                    jsonEachMenu["contents"][1]["text"] = a[prop] if a[prop]!="" else "(empty)"
                    message['contents'].append(jsonEachMenu)
            jsonData['messages'][0]['contents']['body']['contents'].append(message)

    jsonData['messages'][0]['contents']['footer']['contents'][0]['action']['uri'] = "https://ship-assistant.web.app/log/"+data['logId']+"?utm_source=line_"+date+"&utm_medium=LINE"

    betaheaders = {
        'Authorization': 'Bearer ' + LINE_BETA_CHANNEL_ACCESS_TOKEN,
        'Content-type': 'application/json'
    }
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
    if flag:
        logMessage = ""
        betaresponse = requests.post(broadcastEndPoint, json=jsonData, headers=betaheaders)
        if betaresponse.status_code != 200:
            logMessage += "Something error happend on LINE beta. \n\n[error message]\n"+ betaresponse.text
        else:
            logMessage += "Send message succeed on LINE beta."
        response = requests.post(broadcastEndPoint, json=jsonData, headers=headers)
        if response.status_code != 200:
            logMessage += "Something error happend on LINE main. \n\n[error message]\n"+ response.text
        else:
            logMessage += "Send message succeed on LINE main."
        subresponse = requests.post(broadcastEndPoint, json=jsonData, headers=subheaders)
        if subresponse.status_code != 200:
            logMessage += "Something error happend on LINE sub. \n\n[error message]\n"+ subresponse.text
        else:
            logMessage += "Send message succeed on LINE sub."
        print(logMessage)

        return logMessage

if __name__ == "__main__":
    main()