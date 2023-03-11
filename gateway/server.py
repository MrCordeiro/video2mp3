import json

import gridfs
import pika
from flask import Flask, request
from flask_pymongo import PyMongo

from gateway.auth import login, validate_token
from gateway.storage import upload_file

server = Flask(__name__)
# Access mongodb located on the dev environment
# FIXME: Replace with environment variable
server.config["MONGO_URI"] = "mongodb://host.minikube.internal:27017/videos"

# Flask wrapper that manages mongodb connections
mongo = PyMongo(server)

# GridFS is a specification for storing and retrieving files that exceed the
# BSON-document size limit of 16 MB.
fs = gridfs.GridFS(mongo.db)

# RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()


# Routes
@server.route("/login", methods=["POST"])
def login_route():
    token, err = login(request)
    if err:
        return err
    return token


@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate_token(request)
    if err:
        return err

    access = json.loads(access)
    if not access["admin"]:
        return "Unauthorized", 401

    if len(request.files) != 1:
        return "Only one file can be uploaded at a time", 400

    for _, file in request.files.items():
        # This should only be called once since we only have one file
        err = upload_file(file, fs, channel, access)
        if err:
            return err
        return "File uploaded successfully", 200


@server.route("/download", methods=["GET"])
def download():
    pass


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
