import os


def pytest_sessionstart(session):
    os.environ.setdefault("SECRET_ENTRY_PASSWORD", "test-entry")
    os.environ.setdefault("SECRET_USER_1", "user_alpha")
    os.environ.setdefault("SECRET_PASS_1", "$2b$12$w6Qm8qHdzvkn8jc9Y7sRl.Z7So4ZYYMVeMccza8R7QhZQvVwPuE4K")
    os.environ.setdefault("SECRET_USER_2", "user_beta")
    os.environ.setdefault("SECRET_PASS_2", "$2b$12$w6Qm8qHdzvkn8jc9Y7sRl.Z7So4ZYYMVeMccza8R7QhZQvVwPuE4K")
    os.environ.setdefault("JWT_SECRET", "test-jwt-secret-test-jwt-secret-test-jwt-secret")
    os.environ.setdefault("ENCRYPTION_KEY", "test-encryption-key-test-encryption-key")
