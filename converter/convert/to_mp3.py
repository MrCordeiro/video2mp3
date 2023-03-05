"""Video to mp3 converter"""
import json
import os
import tempfile
from typing import Optional

import pika
from bson.objectid import ObjectId
from gridfs import GridFS
from moviepy.editor import VideoFileClip


def _convert_video_to_mp3(video_info, fs_videos, file):
    """Collects video from MongoDB and converts it to mp3"""
    # We can't take the file from MongoDB just with its id, we need to convert
    # it to an bson object first
    video_bytes = fs_videos.get(ObjectId(video_info["video_fid"]))
    # Write the video file from Mongo to a temporary file
    file.write(video_bytes.read())
    audio = VideoFileClip(file.name).audio
    return audio


def start(
    message: bytes, fs_videos: GridFS, fs_mp3s: GridFS, channel: pika.BlockingConnection
) -> Optional[str]:
    """
    Converts video to mp3, saves it to mongo and publishes message to mp3 queue
    """
    video_info = json.loads(message)
    with tempfile.NamedTemporaryFile() as temp_file:
        audio = _convert_video_to_mp3(video_info, fs_videos, temp_file)

    # Write audio to the file
    tf_path = tempfile.gettempdir() + f"/{video_info['video_fid']}.mp3"
    audio.write_audiofile(tf_path)

    # Save file to mongo
    with open(tf_path, "rb") as file:
        data = file.read()
        fid = fs_mp3s.put(data)
    os.remove(tf_path)

    video_info["mp3_fid"] = str(fid)

    try:
        channel.basic_publish(
            exchange="",
            routing_key=os.getenv("MP3_QUEUE"),
            body=json.dumps(video_info),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as err:
        # Delete file from mongo if publishing fails so that we don't have
        # orphaned files
        fs_mp3s.delete(fid)
        return f"Failed to publish message: {err}"
    return None
