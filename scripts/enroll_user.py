#!/usr/bin/env python3
import argparse
import bcrypt


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate bcrypt password hash for Pixel Notes secret users")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    hashed = hash_password(args.password)
    print(f"USERNAME={args.username}")
    print(f"HASH={hashed}")


if __name__ == "__main__":
    main()
