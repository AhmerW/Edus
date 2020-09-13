import secrets
import string

CHOICES = string.ascii_letters+string.digits

def randUid(length :  int = 20):
    return int(''.join(secrets.choice(string.digits) for _ in range(length)))
    
def randToken(length : int = 20):
    return ''.join(secrets.choice(CHOICES) for _ in range(length))
