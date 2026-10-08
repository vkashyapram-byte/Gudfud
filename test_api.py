import urllib.request
import json

req = urllib.request.Request('http://localhost:8000/v1/catalogue?page=1&size=1')
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
    print(json.dumps(data, indent=2))
