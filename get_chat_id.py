import requests

TOKEN = "1234567890:ABCdef..."  # Colle TON token
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

# 1. Envoie /start à ton bot
resp = requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id=@TonUsername&text=/start")
print("START envoyé")

# 2. Attend et récupère
import time
time.sleep(3)
r = requests.get(url)
print(r.json())

# 3. Trouve "chat":{"id":123456789} 👈 TON ID
