import urllib.request
import urllib.error

url = 'http://127.0.0.1:8000/api/v1/repositories'

# Test OPTIONS request with port 3002 origin
req = urllib.request.Request(url, method='OPTIONS')
req.add_header('Origin', 'http://localhost:3002')
req.add_header('Access-Control-Request-Method', 'GET')
req.add_header('Access-Control-Request-Headers', 'x-request-id')

try:
    with urllib.request.urlopen(req) as response:
        print("Status:", response.status)
        print("Headers:")
        for k, v in response.getheaders():
            print(f"  {k}: {v}")
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("Reason:", e.reason)
    print("Response headers:")
    for k, v in e.headers.items():
        print(f"  {k}: {v}")
    try:
        print("Response body:", e.read().decode())
    except Exception as read_err:
        print("Could not read body:", read_err)
except Exception as e:
    print("Other Error:", e)
