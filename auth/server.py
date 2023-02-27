"""Server for auth microservice."""

import os
from datetime import datetime, timedelta, timezone

import psycopg2
from flask import Flask, request
from jwt import decode, encode, exceptions

server = Flask(__name__)


def get_db_connection():
    """Get a connection to the database."""
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        port=os.getenv("POSTGRES_PORT"),
    )
    return conn


@server.route("/login", methods=["POST"])
def login():
    """Login a user and return a JWT token."""
    auth = request.authorization
    if not auth:
        return "Missing credentials", 401

    conn = get_db_connection()
    cur = conn.cursor()
    res = cur.execute(f"SELECT email, password FROM user WHERE email='{auth.username}'")
    cur.close()
    conn.close()
    if res <= 0:
        return "Invalide credentials", 401

    user_row = cur.fetchone()
    email = user_row[0]
    password = user_row[1]
    if auth.username != email or auth.password != password:
        return "Invalid credentials", 401

    return create_jwt(auth.username, os.getenv("JWT_SECRET"), True)


@server.route("/validate", methods=["POST"])
def validate():
    """Validate a JWT token."""

    encoded_jwt = request.headers["Authorization"]
    if not encoded_jwt:
        return "Missing credentials", 401
    encoded_jwt = encoded_jwt.split(" ")[1]

    try:
        decoded = decode(encoded_jwt, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    except exceptions.InvalidTokenError:
        return "Not authorized", 403
    return decoded, 200


def create_jwt(username, secret, is_admin):
    """Create a JWT token."""
    return encode(
        {
            "username": username,
            "exp": datetime.now(tz=timezone.utc) + timedelta(days=1),
            "iat": datetime.utcnow(),
            "admin": is_admin,
        },
        secret,
        algorithm="HS256",
    )


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)
