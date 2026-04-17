import requests
import json

url = "http://127.0.0.1:5000/api/generate-quiz"
data = {
    "text": "The requests library in Python is a popular HTTP library that makes it easy to send HTTP/1.1 requests.",
    "numQs": 2,
    "qType": "MCQ",
    "numOpts": 3,
    "incAns": True,
    "incExp": True
}
response = requests.post(url, json=data)
print("Status:", response.status_code)
print("Response:", response.text)
