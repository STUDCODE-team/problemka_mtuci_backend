import random

from passlib.hash import bcrypt


def hash_value(value: str) -> str:
    return bcrypt.hash(value)


def verify_hash(value: str, hashed: str) -> bool:
    return bcrypt.verify(value, hashed)


def generate_value(length: int) -> str:
    start = 10 ** (length - 1)
    end = 10 ** length - 1
    return str(random.randint(start, end))
