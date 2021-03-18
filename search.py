import os
import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.environ['DATABASE_URL']


def main(id):
    data = []
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT link FROM con_high WHERE id = %s',
                        [id])
            result = cur.fetchall()
            for item in result:
                data.append([item[0]])
            cur.execute('SELECT link FROM study_high WHERE id = %s', [id])
            result = cur.fetchall()
            for item in result:
                data.append([item[0]])
        conn.commit()
    return data


def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')


if __name__ == "__main__":
    main()
