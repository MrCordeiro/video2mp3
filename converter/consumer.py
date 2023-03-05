"""
Consumer for the video queue. Converts videos to mp3s and stores them in the
mp3s database.
"""
import os
import sys

import gridfs
import pika
from pymongo import MongoClient

from convert import to_mp3


def main() -> None:
    """Main function for the consumer."""

    client = MongoClient("host.minikube.internal", 27017)
    db_videos = client.videos
    db_mp3s = client.mp3s
    fs_videos = gridfs.GridFS(db_videos)
    fs_mp3s = gridfs.GridFS(db_mp3s)

    # Rabbitmq connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()

    def callback(channel, method, properties, body):
        """Runs to_mp3.start() and acks or nacks the message."""
        err = to_mp3.start(body, fs_videos, fs_mp3s, channel)
        if err:
            # nack = negative acknowledgement
            # We want to keep messages that fail to convert in the queue
            # so that we can process them later.
            channel.basic_nack(delivery_tag=method.delivery_tag)
        else:
            # ack = acknowledgement
            # The delivery_tag is a unique identifier for the message. 
            # RabbitMQ uses this in order to remove the message from the queue.
            channel.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=os.environ.get("VIDEO_QUEUE"), on_message_callback=callback
    )

    print("Waiting for messages. To exit press CTRL+C")

    # Starts listening for messages in the queue
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        sys.exit(0)
