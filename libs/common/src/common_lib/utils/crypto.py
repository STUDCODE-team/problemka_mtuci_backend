import hashlib
import hmac
import random


def hash_value(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def verify_hash(value: str, hashed: str) -> bool:
    return hmac.compare_digest(hashlib.sha256(value.encode()).hexdigest(), hashed)


def generate_value(length: int) -> str:
    start = 10 ** (length - 1)
    end = 10 ** length - 1
    return str(random.randint(start, end))
