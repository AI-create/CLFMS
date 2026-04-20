import requests, json
r = requests.post("http://127.0.0.1:8000/api/v1/auth/login", json={"email": "admin@clfms.local", "password": "admin123"})
token = r.json()["data"]["token"]
r2 = requests.get("http://127.0.0.1:8000/api/v1/dashboard/top-projects", headers={"Authorization": "Bearer " + token})
print("Status:", r2.status_code)
print(json.dumps(r2.json(), indent=2))
import requests
r = requests.post("http://127.0.0.1:8000/api/v1/auth/login", json={"email": "admin@clfms.local", "password": "admin123"})
token = r.json()["data"]["token"]
r2 = requests.get("http://127.0.0.1:8000/api/v1/dashboard/top-projects", headers={"Authorization": "Bearer " + token})
print("Status:", r2.status_code)
for p in r2.json().get("data", []):
    print("  " + p["project_name"] + ": income=" + str(p["income"]) + ", expense=" + str(p["expense"]) + ", profit=" + str(p["profit"]))
