import requests
import datetime

def main():
    eventInfo = requests.get('https://sekai-world.github.io/sekai-master-db-diff/events.json').json()
    event = {
        "name": eventInfo[-1]["name"],
        "id": eventInfo[-1]["id"],
        "start": eventInfo[-1]["startAt"],
        "end": eventInfo[-1]["aggregateAt"]
    }
    ranking = requests.get('https://api.sekai.best/event/live?region=jp').json()
    if ranking["status"] == "success":
        message = str(datetime.datetime.strptime(ranking["data"]["eventRankings"][0]["timestamp"][:-5], "%Y-%m-%dT%H:%M:%S") + datetime.timedelta(hours=9)) + "のスコア"
        message += "(あと:" + str((datetime.datetime.fromtimestamp(event["end"]//1000) - datetime.datetime.strptime(ranking["data"]["eventRankings"][0]["timestamp"][:-5], "%Y-%m-%dT%H:%M:%S")) - datetime.timedelta(hours=9)) + ") \n"
        maxlen = len(str(ranking["data"]["eventRankings"][0]["score"]))
        for eachPlayer in sorted(ranking["data"]["eventRankings"], key=lambda x: x["rank"]):
            message += "``" + "".join([" "]*(6 - len(str(eachPlayer["rank"])))) + str(eachPlayer["rank"]) + "``位:  ``" +  "".join([" "]*(maxlen - len(str(eachPlayer["score"])))) + str(eachPlayer["score"]) + "`` - " + eachPlayer["userName"] + "\n"
            print(message)
        return [message, event]
    else:
        return ["error"]


if __name__ == "__main__":
    main()
