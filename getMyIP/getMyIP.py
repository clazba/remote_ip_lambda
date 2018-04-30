# remIp.py

from flask import request
from flask import jsonify
from flask import Flask

app = Flask(__name__)

@app.route("/getMyIP", methods=["GET"])
def get_my_ip():
    return jsonify({'ip': request.remote_addr}), 200

#if __name__ == '__main__':
#    app.run(debug=False)
