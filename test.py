import secrets
import string
import datetime

def generate_token_with_timestamp(length=30, valid_minutes=5):
    characters = string.ascii_letters + string.digits  # ascii_letters: 所有英文字母；digits: 所有數字
    token = ''.join(secrets.choice(characters) for _ in range(length))
    
    timestamp = datetime.datetime.now().isoformat()
    
    return {
        "token": token,
        "timestamp": timestamp,
        "valid_minutes": valid_minutes
    }

if __name__ == "__main__":
    token_info = generate_token_with_timestamp(length=30, valid_minutes=5)
    print(token_info)