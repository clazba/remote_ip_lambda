#rds_db.py
import logging
import pymysql.cursors
from dotenv import load_dotenv, find_dotenv


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

