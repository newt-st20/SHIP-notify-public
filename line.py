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
    getDatetime = datetime.datetime.now().strftime("%y/%m/%d") + " " + str(data['getTime'])
    jsonTemplete = json.load(open('json/push.json', 'r', encoding="utf-8_sig"))
    payload = jsonTemplete['flexMessage']
    payload['messages'][0]['contents']['body']['contents'][2]['text'] = "Fetch: " + getDatetime

    notifyFlag = False
    altText = ""
    for i, channelInfo in enumerate(jsonTemplete['channelList']):
        channel = data[channelInfo['name']]
        if len(channel) != 0:
            channelflag = False
            message = copy.deepcopy(jsonTemplete['channel'])
            message['contents'][0]['text'] = channelInfo['jpName']
            propNames = json.load(open('json/ship.json', 'r', encoding="utf-8_sig"))['pageList'][i]['lineProps']
            for post in channel:
                postFlag = True
                eachPost = []
                for propName in propNames:
                    propJson = copy.deepcopy(jsonTemplete['prop'])
                    propJson["contents"][0]["text"] = propName if propName != "description" else "detail"
                    if ("高１" in post[propName] or "高1" in post[propName] or "高３" in post[propName] or "高3" in post[propName]) and ("高２" not in post[propName] and "高2" not in post[propName]):
                        postFlag = False
                        break
                    else:
                        if propName == "folder" and post[propName] == "":
                            propJson["contents"][1]["text"] = "(root)"
                        else:
                            propJson["contents"][1]["text"] = post[propName]
                        eachPost.append(propJson)
                if postFlag:
                    channelflag = True
                    notifyFlag = True
                    eachPost.append(jsonTemplete["separate"])
                    message['contents'].extend(eachPost)
            if channelflag:
                payload['messages'][0]['contents']['body']['contents'].append(message)
                altText += "[" + channelInfo['jpName'] + "]"
    
    payload['messages'][0]['altText'] = altText + "に更新がありました"
    payload['messages'][0]['contents']['footer']['contents'][0]['action']['uri'] = "https://ship-assistant.web.app/log/"+data['logId']+"?utm_source=line_"+date+"&utm_medium=LINE"

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
    print(payload)
    if notifyFlag:
        logMessage = ""
        betaresponse = requests.post(broadcastEndPoint, json=payload, headers=betaheaders)
        if betaresponse.status_code != 200:
            logMessage += "\nSomething error happend on LINE beta. [error message]"+ betaresponse.text
        else:
            logMessage += "\nSend message succeed on LINE beta."
        logMessage += "\n\npayload length:" + str(len(str(payload)))
        if os.environ['STATUS'] == "remote":
            response = requests.post(broadcastEndPoint, json=payload, headers=headers)
            if response.status_code != 200:
                logMessage += "\nSomething error happend on LINE main. [error message]"+ response.text
            else:
                logMessage += "\nSend message succeed on LINE main."
            subresponse = requests.post(broadcastEndPoint, json=payload, headers=subheaders)
            if subresponse.status_code != 200:
                logMessage += "\nSomething error happend on LINE sub. [error message]"+ subresponse.text
            else:
                logMessage += "\nSend message succeed on LINE sub."
        logMessage += "\n\njsonData length:" + str(len(str(payload)))
        print(logMessage)
        return logMessage
    else:
        return "@advanced-info 他学年通知削減システムによりメッセージは配信されませんでした"

if __name__ == "__main__":
    main()