import re
from app.utils.key_generator import generate_key_code, generate_batch_key_codes


def test_generate_key_code_format():
    code = generate_key_code()
    assert len(code) == 19
    assert re.match(r"^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$", code)


def test_generate_key_code_uniqueness():
    codes = {generate_key_code() for _ in range(1000)}
    assert len(codes) == 1000


def test_generate_batch_key_codes():
    codes = generate_batch_key_codes(100)
    assert len(codes) == 100
    assert len(set(codes)) == 100


def test_generate_batch_key_codes_format():
    codes = generate_batch_key_codes(10)
    for code in codes:
        assert len(code) == 19
        assert re.match(r"^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$", code)
