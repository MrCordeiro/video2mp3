import json

import gridfs
import pika
from bson.objectid import ObjectId
from flask import Flask, request, send_file
from flask_pymongo import PyMongo

from gateway.auth import login, validate_token
from gateway.storage import upload_file

server = Flask(__name__)

# Flask wrapper that manages mongodb connections
mongo_video = PyMongo(server, uri="mongodb://host.minikube.internal:27017/videos")
mongo_mp3 = PyMongo(server, uri="mongodb://host.minikube.internal:27017/mp3s")

# GridFS is a specification for storing and retrieving files that exceed the
# BSON-document size limit of 16 MB.
fs_videos = gridfs.GridFS(mongo_video.db)
fs_mp3s = gridfs.GridFS(mongo_mp3.db)

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
    """Uploads a video file and sends a message to the video queue"""
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
        err = upload_file(file, fs_videos, channel, access)
        if err:
            return err
        return "File uploaded successfully", 200


@server.route("/download", methods=["GET"])
def download():
    """Downloads a mp3 file given its fid"""
    access, err = validate_token(request)
    if err:
        return err

    access = json.loads(access)
    if not access["admin"]:
        return "Unauthorized", 401
    
    fid = request.args.get("fid")
    if not fid:
        return "Missing parameter: 'fid'", 400
    try:
        file = fs_mp3s.get(ObjectId(fid))
        return send_file(file, download_name=f"{fid}.mp3")
    except Exception as err:
        return f"Internal server error: {err}", 500


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
