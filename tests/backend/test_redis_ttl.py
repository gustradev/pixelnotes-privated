import fakeredis

from app.redis_client import redis_client


def test_chat_key_ttl_enforced():
    fake = fakeredis.FakeRedis(decode_responses=True)
    redis_client._client = fake

    redis_client.add_message("user_alpha", "encrypted-message")
    ttl = fake.ttl("chat:room:global")

    assert ttl > 0
    assert ttl <= 86400
