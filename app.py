# app.py
import os
from flask import Flask, Response, json, request
from rds_db import build_db build_response

app = Flask(__name__)

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
    query = """insert into User (ID, FirstName, LastName, Email)
            values(%s, %s, %s, %s)
            """
    return (query, (uniq_id, data["first_name"], data["last_name"], data["email"]))

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

@app.route('/build', methods=["GET"])
def build():
    return build_db()

# include this for local dev
if __name__ == '__main__':
    app.run()
