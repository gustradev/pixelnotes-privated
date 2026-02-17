from app.auth import AuthHandler


def test_create_and_decode_token_roundtrip():
    token = AuthHandler.create_token("user_alpha")
    payload = AuthHandler.decode_token(token)
    assert payload is not None
    assert payload["sub"] == "user_alpha"
    assert payload["type"] == "access"


def test_invalid_token_rejected():
    payload = AuthHandler.decode_token("invalid.token.value")
    assert payload is None
