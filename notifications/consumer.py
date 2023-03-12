"""
Consumer for the mp3 queue.
Sends an email to the user when the mp3 file is ready.
"""
import json
import os
import smtplib
import sys
from email.message import EmailMessage

import pika


def _send_email(message: str) -> None:
    message = json.loads(message)
    mp3_fid = message["mp3_fid"]
    sender_address = os.getenv("GMAIL_ADDRESS")
    sender_password = os.getenv("GMAIL_PASSWORD")
    receiver_address = message["username"]

    msg = EmailMessage()
    msg.set_content(f"mp3 file_id: {mp3_fid} is now ready!")
    msg["Subject"] = "MP3 Download"
    msg["From"] = sender_address
    msg["To"] = receiver_address

    with smtplib.SMTP("smtp.gmail.com", 587) as session:
        session.starttls()
        session.login(sender_address, sender_password)
        session.send_message(msg, sender_address, receiver_address)
    print("Mail Sent")

    
def main() -> None:
    """Main function for the consumer."""

    # Rabbitmq connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()

    def callback(channel, method, properties, body):
        try:
            _send_email(body)
        except Exception:
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
        queue=os.getenv("MP3_QUEUE"), on_message_callback=callback
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
