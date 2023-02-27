import json
from datetime import datetime
from typing import Union

import pika
from gridfs import GridFS
from werkzeug.datastructures import FileStorage


def upload_file(
    file: FileStorage,
    fs: GridFS,
    channel: pika.BlockingConnection,
    access: dict[str, Union[str, datetime]],
) -> str:
    """Upload a file to the database and send a message to the video queue."""
    try:
        fid = fs.put(file)
    except Exception as err:
        return f"Internal server error: {err}", 500

    message = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": access["username"],
    }

    try:
        # Send message to the video queue
        # The exchange is empty because we are using a default exchange
        # The role of the exchange is to allocate the message is to the right
        # queue
        # PERSISTENT_DELIVERY_MODE makes sure that the message is not lost
        # if a pode restarts or crashes
        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as err:
        # If the message fails to be sent, delete the file from the database
        # so that there are not stale files in the database
        fs.delete(fid)
        return f"Internal server error: {err}", 500
