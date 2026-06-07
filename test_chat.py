import requests

url = "https://student-management-system-rosy-delta.vercel.app/students/chat"
headers = {"Content-Type": "application/json"}
data = {"question": "What is her ID?"}

response = requests.post(url, headers=headers, json=data)
print("Status Code:", response.status_code)
print("Response:", response.text)
