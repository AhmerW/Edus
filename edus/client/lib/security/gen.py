import secrets
import string

def randUid(length :  int = 20):
    return int(''.join(secrets.choice(string.digits) for _ in range(length)))
