import requests

API_URL = "http://127.0.0.1:8000/request-ride/"

def submit_ride(user_id, source, dest):
    payload = {
        "user_id": user_id,
        "source_location": source,
        "dest_location": dest
    }
    response = requests.post(API_URL, json=payload)
    print("📩 Server Response:", response.json())

if __name__ == "__main__":
    submit_ride(101, "Whitefield", "Hebbal")
