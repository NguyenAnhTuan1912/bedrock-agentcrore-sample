import requests
import json

url = "http://localhost:9000/"

payload = {
    "jsonrpc": "2.0",
    "id": "req-001",
    "method": "message/send",
    "params": {
        "message": {
            "role": "user",
            "parts": [{"kind": "text", "text": "what is 101 * 11?"}],
            "messageId": "12345678-1234-1234-1234-123456789012",
        }
    },
}

headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)

print(json.dumps(response.json(), indent=2))
