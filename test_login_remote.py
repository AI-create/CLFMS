import urllib.request, json
data = json.dumps({"email":"admin@clfms.local","password":"AdminClfms2026"}).encode()
req = urllib.request.Request("http://localhost:8080/api/v1/auth/login", data=data, headers={"Content-Type":"application/json"})
try:
    resp = urllib.request.urlopen(req).read().decode()
    d = json.loads(resp)
    print("Login OK:", d.get("success"), "| Role:", d.get("data",{}).get("user",{}).get("role"))
    print("Token present:", bool(d.get("data",{}).get("token")))
except Exception as e:
    print("ERROR:", e)
