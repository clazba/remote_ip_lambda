# app.py
import os
from flask import Flask, Response, json, request
import logging
import pymysql.cursors
from dotenv import load_dotenv, find_dotenv
import uuid

app = Flask(__name__)



# Adding a post/get route is pretty straightforward with flask, let's add one for getting a fake user
# Adding a post/get route is pretty straightforward with flask, let's add one for getting a fake user
@app.route('/user', methods=["GET", "POST"])
def user():
    conn = connect()
    if request.method == "GET":
        items = []
        try:
            with conn.cursor() as cur:
                cur.execute("select * from User")
                for row in cur:
                    items.append(row)
                conn.commit()
        except Exception as e:
            logger.info(e)
            response = build_response({"status": "error", "message": "error getting users"}, 500)
            return response
        finally:
            conn.close()
        response = build_response({"rows": items, "status": "success"}, 200)
        return response
    if request.method == "POST":
        data = {
            "first_name": request.form.get("first_name", ""),
            "last_name": request.form.get("last_name", ""),
            "email": request.form.get("email", "")
        }
        valid, fields = validate(data)
        if not valid:
            error_fields = ', '.join(fields)
            error_message = "Data missing from these fields: %s" %error_fields
            return build_response({"status": "error", "message": error_message}, 400)
        query, vals = insert(data)
        try:
            with conn.cursor() as cur:
                cur.execute(query, vals)
                conn.commit()
        except Exception as e:
            logger.exception("insert error")
            return build_response({"status": "error", "message": "insert error"}, 500)
        finally:
            conn.close()
            cur.close()
        return build_response({"status": "success"}, 200)
# Input validation for GET data entry

def validate(data):
    error_fields = []
    not_null = [
        "first_name",
        "last_name",
        "email"
    ]

    for x in not_null:
        if x not in data or len(data[x]) == 0:
            error_fields.append(x)
    return (len(error_fields) == 0, error_fields)

def insert(data):
    uniq_id = str(uuid5(uuid1(), str(uuid1())))
    query = """insert into User (ID, FirstName, LastName, Email)values(%s, %s, %s, %s)"""
    return (query, (uniq_id, data["first_name"], data["last_name"], data["email"]))

@app.route('/build', methods=["GET"])
def build():
    return build_db()
# first, load your env file, replacing the path here with your own if it differs
# when using the local database make sure you change your path  to .dev.env, it should work smoothly.
load_dotenv()

# we need to instantiate the logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
#dotenv = Dotenv(os.path.join(os.path.dirname(__file__), ".env"))
# update environment just in case
#os.environ.update(dotenv)
# set globals
RDS_HOST = os.getenv("DB_HOST")
RDS_PORT = int(os.getenv("DB_PORT", 3306))
NAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


def connect():
    try:
        cursor = pymysql.cursors.DictCursor
        conn = pymysql.connect(RDS_HOST, user=NAME, passwd=PASSWORD, db=DB_NAME, port=RDS_PORT, cursorclass=cursor, connect_timeout=5)
        logger.info("SUCCESS: connection to RDS successful")
        return(conn)
    except Exception as e:
        logger.exception("Database Connection Error")

# Function to build the user table
def build_db():
    conn = connect()
    query = "create table User (ID varchar(255) NOT NULL, firstName varchar(255) NOT NULL, lastName varchar(255) NOT NULL, email varchar(255) NOT NULL, PRIMARY KEY (ID))"
    try:
        with conn.cursor() as cur:
            # just in case it doesn't work the first time let's drop the table if it exists
            cur.execute("drop table if exists User")
            cur.execute(query)
            conn.commit()
    except Exception as e:
        logger.exception(e)
        response = Respone(json.dumps({"status": "error", "message": "could not build table"}), 500)
    finally:
        cur.close()
        conn.close()
    response = Response(json.dumps({"status": "success"}), 200)
    return response

# Posting to the database with form data. First, let's break out our response building into a function:
def build_response(resp_dict, status_code):
    response = Response(json.dumps(resp_dict), status_code)
    return response
# include this for local dev
if __name__ == '__main__':
    app.run()
