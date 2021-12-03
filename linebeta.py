import copy
import json
import os
import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

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
                    if ("高２" in post[propName] or "高2" in post[propName] or "高３" in post[propName] or "高3" in post[propName]) and ("高１" not in post[propName] and "高1" not in post[propName]):
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
        print(logMessage)
        return logMessage
    else:
        return "他学年通知削減システムによりメッセージは配信されませんでした"

if __name__ == "__main__":
    main()