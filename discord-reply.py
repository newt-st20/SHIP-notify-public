import os
from oauth2client.service_account import ServiceAccountCredentials
import json
import gspread
import requests
import re
import datetime
import discord

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

TOKEN = os.environ['DISCORD_TOKEN']
client = discord.Client()


@client.event
async def on_ready():
    print('Discordにログインしました')


@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content == '/neko':
        await message.channel.send('にゃーん')
    if message.content == '/about':
        messageSheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('message')
        messageData = messageSheet.cell(1, 2).value
        await message.channel.send(messageData)
    if message.content == '/connection':
        connectionSheet = gc.open_by_key(
            SPREADSHEET_KEY).worksheet('connection')
        connectionSheetLow = len(connectionSheet.col_values(1))
        newestConnection = connectionSheet.cell(
            connectionSheetLow, 2).value[1:-1]
        newestConnectionList = re.findall('\[(.*?)\]', newestConnection)
        newestConnectionBaseMessage = ""
        print(newestConnectionList)
        for connectionEach in newestConnectionList:
            newestConnectionBaseMessage += "\n・" + re.findall("\'(.*?)\'", connectionEach)[0].replace("\\n", "").replace("\\u3000", " ") + "-" + re.findall(
                "\'(.*?)\'", connectionEach)[1].replace("\\n", "").replace("\\u3000", " ") + "-" + re.findall("\'(.*?)\'", connectionEach)[2].replace("\\n", "").replace("\\u3000", " ")
            if re.findall("\'(.*?)\'", connectionEach)[3].replace("\\n", "").replace("\\u3000", " ") != "":
                newestConnectionBaseMessage += "\n《" + \
                    re.findall(
                        "\'(.*?)\'", connectionEach)[3].replace("\\n", "").replace("\\u3000", " ") + "》"
        print(newestConnectionBaseMessage)
        newestConnectionTime = connectionSheet.cell(
            connectionSheetLow, 3).value
        lastUpdateConnectionTime = connectionSheet.cell(
            connectionSheetLow, 4).value
        if lastUpdateConnectionTime == "":
            lastUpdateConnectionTime = newestConnectionTime
        newestConnectionMessage = "連絡事項最終更新:" + \
            newestConnectionTime.replace("-", "/") + "\n連絡事項最終取得:" + \
            lastUpdateConnectionTime.replace("-", "/") + "\n" + \
            str(newestConnectionBaseMessage)
        await message.channel.send(newestConnectionMessage)
    if message.content == '/study':
        studySheet = gc.open_by_key(
            SPREADSHEET_KEY).worksheet('study')
        studySheetLow = len(studySheet.col_values(1))
        newestStudy = studySheet.cell(
            studySheetLow, 2).value[1:-1]
        newestStudyList = re.findall('\[(.*?)\]', newestStudy)
        newestStudyBaseMessage = ""
        print(newestStudyList)
        for studyEach in newestStudyList:
            newestStudyBaseMessage += "\n・" + re.findall("\'(.*?)\'", studyEach)[0].replace("\\n", "").replace("\\u3000", " ") + "-" + re.findall(
                "\'(.*?)\'", studyEach)[1].replace("\\n", "").replace("\\u3000", " ") + "-" + re.findall("\'(.*?)\'", studyEach)[2].replace("\\n", "").replace("\\u3000", " ")
        print(newestStudyBaseMessage)
        newestStudyTime = studySheet.cell(
            studySheetLow, 3).value
        lastUpdateStudyTime = studySheet.cell(
            studySheetLow, 4).value
        if lastUpdateStudyTime == "":
            lastUpdateStudyTime = newestStudyTime
        newestStudyMessage = "学習教材最終更新:" + \
            newestStudyTime.replace("-", "/") + "\n学習教材最終取得:" + \
            lastUpdateStudyTime.replace("-", "/") + "\n" + \
            str(newestStudyBaseMessage)
        await message.channel.send(newestStudyMessage)


client.run(TOKEN)
