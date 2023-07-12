import requests
import base64

url = 'https://api-seller.rozetka.com.ua/sites'
username = 'danyla958@gmail.com'
password = '3ke4pr'

# Encode the password in base64
encoded_password = base64.b64encode(password.encode('utf-8')).decode('utf-8')

# Create the request body
data = {
    'username': username,
    'password': encoded_password
}

# Send the POST request
response = requests.post(url, json=data)

print(response.status_code)
print(response.json())
