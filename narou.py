import datetime
import os
import random
import re
import time
import requests

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import DictCursor

load_dotenv()

DATABASE_URL = os.environ['DATABASE_URL']


def main():
    data = []
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT ncode, lastup, count, title FROM narou WHERE ended = 1')
            result = cur.fetchall()
            for item in result:
                response = requests.get(
                    'https://api.syosetu.com/novelapi/api/?out=json&ncode='+item[0]+'&of=t-gl-ga-e')
                responseJson = response.json()
                lastUpdate = responseJson[1]['general_lastup']
                count = responseJson[1]['general_all_no']
                end = responseJson[1]['end']
                if item[1] != lastUpdate:
                    data.append([item[0], lastUpdate, count, item[3]])
                    cur.execute(
                        'UPDATE narou SET lastup = (%s), count = (%s), ended = (%s) WHERE ncode = (%s)', [lastUpdate, count, end, item[0]])
        conn.commit()
    return data


def add(ncode):
    response = requests.get(
        'https://api.syosetu.com/novelapi/api/?out=json&ncode='+ncode+'&of=t-gl-ga-e')
    try:
        responseJson = response.json()
        title = responseJson[1]['title']
        lastUpdate = responseJson[1]['general_lastup']
        count = responseJson[1]['general_all_no']
        end = responseJson[1]['end']
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO narou (title, ncode, lastup, count, ended) VALUES (%s, %s, %s, %s, %s)', [
                    title, ncode, lastUpdate, count, end])
            conn.commit()
    except Exception as e:
        print(str(e))
        return ["error", str(e)]
    return ["success", title, "https://ncode.syosetu.com/"+ncode]


def remove(ncode):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT ncode, lastup, count, title FROM narou')
                result = cur.fetchall()
                if len(result) != 0:
                    try:
                        cur.execute(
                            'DELETE FROM narou WHERE ncode = %s', [ncode])
                    except Exception as e:
                        return str(e)
            conn.commit()
    except Exception as e:
        print(str(e))
        return ["error", str(e)]
    return ["success", "https://ncode.syosetu.com/"+ncode]


def list():
    data = []
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT ncode, title FROM narou WHERE ended = 1')
            result = cur.fetchall()
            for item in result:
                data.append([item[0], item[1]])
        conn.commit()
    return data


def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')


if __name__ == "__main__":
    main()
