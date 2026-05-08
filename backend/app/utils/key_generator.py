import random
import string

CHARS = string.ascii_uppercase + string.digits


def generate_key_code() -> str:
    segments = ["".join(random.choices(CHARS, k=4)) for _ in range(4)]
    return "-".join(segments)


def generate_batch_key_codes(count: int) -> list[str]:
    codes: set[str] = set()
    while len(codes) < count:
        codes.add(generate_key_code())
    return list(codes)
