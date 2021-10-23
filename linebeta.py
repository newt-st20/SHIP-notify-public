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
    jsonOpen = open('json/push.json', 'r', encoding="utf-8_sig")
    jsonLoad = json.load(jsonOpen)
    jsonHead = jsonLoad['channelHead']
    jsonData = jsonLoad['flexMessage']
    eachMenu = jsonLoad['eachMenu']
    jsonData['messages'][0]['contents']['body']['contents'][2]['text'] = "Fetch: " + getDatetime
    separate = jsonLoad["separate"]
    channelList = jsonLoad['channelList']

    flag = False
    altText = ""
    for index, channel in enumerate(channelList):
        channelData = data[channel['name']]
        if len(channelData) != 0:
            channelflag = False
            message = copy.deepcopy(jsonHead)
            message['contents'][0]['text'] = channel['jpName']
            props = json.load(open('json/ship.json', 'r', encoding="utf-8_sig"))['pageList'][index]['lineProps']
            for a in channelData:
                propsflag = True
                for prop in props:
                    jsonEachMenu = copy.deepcopy(eachMenu)
                    jsonEachMenu["contents"][0]["text"] = prop if prop != "description" else "detail"
                    if ("高２" in a[prop] or "高2" in a[prop] or "高３" in a[prop] or "高3" in a[prop]) and ("高１" not in a[prop] and "高1" not in a[prop]):
                        propsflag = False
                        break
                    elif a[prop] == "" and prop == "folder":
                        jsonEachMenu["contents"][1]["text"] = "(root)"
                    else:
                        jsonEachMenu["contents"][1]["text"] = a[prop]
                    message['contents'].append(jsonEachMenu)
                if propsflag:
                    channelflag = True
                    flag = True
                    message['contents'].append(separate)
            if channelflag:
                jsonData['messages'][0]['contents']['body']['contents'].append(message)
                altText += "[" + channel['jpName'] + "]"
    
    jsonData['messages'][0]['altText'] = altText + "に更新がありました"
    jsonData['messages'][0]['contents']['footer']['contents'][0]['action']['uri'] = "https://ship-assistant.web.app/log/"+data['logId']+"?utm_source=line_"+date+"&utm_medium=LINE"

    betaheaders = {
        'Authorization': 'Bearer ' + LINE_BETA_CHANNEL_ACCESS_TOKEN,
        'Content-type': 'application/json'
    }
    broadcastEndPoint = "https://api.line.me/v2/bot/message/broadcast"
    print(jsonData)
    if flag:
        logMessage = ""
        betaresponse = requests.post(broadcastEndPoint, json=jsonData, headers=betaheaders)
        if betaresponse.status_code != 200:
            logMessage += "\nSomething error happend on LINE beta. [error message]"+ betaresponse.text
        else:
            logMessage += "\nSend message succeed on LINE beta."
        logMessage += "\n\njsonData length:" + str(len(str(jsonData)))
        print(logMessage)
        return logMessage
    else:
        return "他学年通知削減システムによりメッセージは配信されませんでした"

if __name__ == "__main__":
    main()