from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    FollowEvent, UnfollowEvent, MessageEvent, PostbackEvent, TextMessage, TextSendMessage, TemplateSendMessage, FlexSendMessage, ButtonsTemplate, CarouselTemplate, CarouselColumn, PostbackTemplateAction
)
import os
from oauth2client.service_account import ServiceAccountCredentials
import json
import gspread
import requests
import re
import datetime

app = Flask(__name__)

if os.environ['CHANNEL_TYPE'] == "public":
    YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
    YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
else:
    YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_DEV_CHANNEL_ACCESS_TOKEN"]
    YOUR_CHANNEL_SECRET = os.environ["YOUR_DEV_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credential_list = {
    "type": "service_account",
    "project_id": os.environ['SHEET_PROJECT_ID'],
    "private_key_id": os.environ['SHEET_PRIVATE_KEY_ID'],
    "private_key": os.environ['SHEET_PRIVATE_KEY'].replace('\\n', '\n'),
    "client_email": os.environ['SHEET_CLIENT_EMAIL'],
    "client_id": os.environ['SHEET_CLIENT_ID'],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url":  os.environ['SHEET_CLIENT_X509_CERT_URL']
}
credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    credential_list, scope)
gc = gspread.authorize(credentials)
SPREADSHEET_KEY = '1XylqIA4R8rlIcvA113nEJ_PTYMQTGEBsrsT315glFYM'
if os.environ['CHANNEL_TYPE'] == "staging":
    SPREADSHEET_KEY = '1OwuiunNnZcZ3l2QbnGsricHwSfyWliTpRX68-6W5ji0'


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.reply_token == "00000000000000000000000000000000":
        return
    headers = {
        'Authorization': 'Bearer ' + YOUR_CHANNEL_ACCESS_TOKEN,
        'Content-type': 'application/json'
    }
    jsonOpen = open('reply.json', 'r', encoding="utf-8_sig")
    jsonLoad = json.load(jsonOpen)
    replyEndPoint = "https://api.line.me/v2/bot/message/reply"
    if event.message.text == "!about":
        messageSheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('message')
        messageData = messageSheet.cell(1, 2).value
        jsonData = jsonLoad['about']
        jsonData['replyToken'] = event.reply_token
        jsonData['messages'][0]['text'] = messageData
        print(jsonData)
        requests.post(replyEndPoint, json=jsonData, headers=headers)
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=messageData))
    elif event.message.text == "!command":
        messageSheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('message')
        messageData = messageSheet.cell(2, 2).value
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=messageData))
    elif event.message.text == "!settings":
        messageSheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('message')
        messageData = messageSheet.cell(3, 2).value
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=messageData))
    elif event.message.text == "!when":
        messageSheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('message')
        messageData = messageSheet.cell(4, 2).value
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=messageData))
    elif "!issue" in event.message.text:
        if event.message.text == "!issue":
            line_bot_api.reply_message(event.reply_token, TextSendMessage(
                text="不具合報告・機能改善要望コマンドは「!issue 内容」の形で送ってください"))
        else:
            useridSheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('issue')
            useridSheetLow = len(useridSheet.col_values(1))
            profile = line_bot_api.get_profile(event.source.user_id)
            useridSheet.update_cell(useridSheetLow + 1, 1,
                                    str(event.source.user_id))
            useridSheet.update_cell(
                useridSheetLow + 1, 2, str(event.message.text))
            time = datetime.datetime.fromtimestamp(
                int(event.timestamp) / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')
            useridSheet.update_cell(useridSheetLow + 1, 3, str(time))
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="回答を記録しました。不具合報告・機能改善要望ありがとうございます"))
    elif event.message.text == "!connection":
        connectionSheet = gc.open_by_key(
            SPREADSHEET_KEY).worksheet('connection')
        connectionSheetLow = len(connectionSheet.col_values(1))
        newestConnection = connectionSheet.cell(
            connectionSheetLow, 2).value[1:-1]
        newestConnectionList = re.findall('\[(.*?)\]', newestConnection)
        newestConnectionBaseMessage = ""
        print(newestConnectionList)
        for connectionEach in newestConnectionList:
            newestConnectionBaseMessage += "\n" + re.findall("\'(.*?)\'", connectionEach)[0].replace("\\n", "") + "-" + re.findall(
                "\'(.*?)\'", connectionEach)[1].replace("\\n", "") + "-" + re.findall("\'(.*?)\'", connectionEach)[2].replace("\\n", "")
        print(newestConnectionBaseMessage)
        newestConnectionTime = connectionSheet.cell(
            connectionSheetLow, 3).value
        newestConnectionMessage = "連絡事項最終取得:" + \
            newestConnectionTime + "\n" + \
            newestConnectionBaseMessage.replace("\u3000", "")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=newestConnectionMessage))
    elif event.message.text == "!study":
        studySheet = gc.open_by_key(
            SPREADSHEET_KEY).worksheet('study')
        studySheetLow = len(studySheet.col_values(1))
        newestStudy = studySheet.cell(
            studySheetLow, 2).value[1:-1]
        newestStudyList = re.findall('\[(.*?)\]', newestStudy)
        newestStudyBaseMessage = ""
        print(newestStudyList)
        for studyEach in newestStudyList:
            newestStudyBaseMessage += "\n" + re.findall("\'(.*?)\'", studyEach)[0].replace("\\n", "") + "-" + re.findall(
                "\'(.*?)\'", studyEach)[1].replace("\\n", "") + "-" + re.findall("\'(.*?)\'", studyEach)[2].replace("\\n", "")
        print(newestStudyBaseMessage)
        newestStudyTime = studySheet.cell(
            studySheetLow, 3).value
        newestStudyMessage = "学習教材最終取得:" + \
            newestStudyTime + "\n" + \
            newestStudyBaseMessage.replace("\u3000", "")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=newestStudyMessage))
    elif "!not-change-notify-off" in event.message.text:
        useridSheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('userid')
        useridSheetLow = len(useridSheet.col_values(1))
        cell = useridSheet.findall(str(event.source.user_id))
        blockMessage = "not-change-notify-off"
        for f in cell:
            useridSheet.update_cell(f.row, 5, blockMessage)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="更新がない時の通知をオフにしました。「!not-change-notify-on」コマンドよりオフにできます"))
    elif "!not-change-notify-on" in event.message.text:
        useridSheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('userid')
        useridSheetLow = len(useridSheet.col_values(1))
        cell = useridSheet.findall(str(event.source.user_id))
        blockMessage = "not-change-notify-on"
        for f in cell:
            useridSheet.update_cell(f.row, 5, blockMessage)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="更新がない時の通知をオンにしました。「!not-change-notify-off」コマンドよりオフにできます"))
    elif "!" in event.message.text:
        messageSheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('message')
        messageSheetList = messageSheet.col_values(1)
        messageSheetTextList = messageSheet.col_values(2)
        messageCount = 0
        sendMessage = ""
        for messageEach in messageSheetList:
            messageCount += 1
            if event.message.text in messageEach:
                sendMessage = messageSheetTextList[messageCount-1]
                break
            else:
                pass
        if sendMessage == "":
            sendMessage == "It isn't a command, couldn't understand: " + event.message.text
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=sendMessage))
    else:
        pass
    getlogsSheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('getlogs')
    getlogsSheetLow = len(getlogsSheet.col_values(1))
    getlogsSheet.update_cell(getlogsSheetLow + 1, 1, str(event.source.user_id))
    getlogsSheet.update_cell(getlogsSheetLow + 1, 2, str(event))
    time = datetime.datetime.fromtimestamp(
        int(event.timestamp) / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')
    getlogsSheet.update_cell(getlogsSheetLow + 1, 3, str(time))


@handler.add(FollowEvent)
def handle_follow(event):
    useridSheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('userid')
    useridSheetLow = len(useridSheet.col_values(1))
    profile = line_bot_api.get_profile(event.source.user_id)
    useridSheet.update_cell(useridSheetLow + 1, 1, str(event.source.user_id))
    displayName = profile.display_name
    userData = displayName + "," + str(profile)
    useridSheet.update_cell(useridSheetLow + 1, 2, str(userData))
    time = datetime.datetime.fromtimestamp(
        int(event.timestamp) / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')
    useridSheet.update_cell(useridSheetLow + 1, 3, str(time))
    useridSheet.update_cell(useridSheetLow + 1, 4, "")
    useridSheet.update_cell(useridSheetLow + 1, 5, "not-change-notify-on")
    messageSheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('message')
    messageData = messageSheet.cell(1, 2).value
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text=messageData))


@ handler.add(UnfollowEvent)
def handle_unfollow(event):
    useridSheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('userid')
    useridSheetLow = len(useridSheet.col_values(1))
    cell = useridSheet.findall(str(event.source.user_id))
    time = datetime.datetime.fromtimestamp(
        int(event.timestamp) / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')
    blockMessage = "blocked:" + str(time)
    for f in cell:
        useridSheet.update_cell(f.row, 5, "not-change-notify-off")
        if useridSheet.cell(f.row, 4).value == "":
            useridSheet.update_cell(f.row, 4, blockMessage)


if __name__ == "__main__":
    #    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
