from flask import Flask, render_template, request, redirect, url_for
import hashlib
import time
import random
import requests
from urllib.parse import quote

app = Flask(__name__)

def getxg(param, data):
    ttime = int(time.time())
    url_md5 = hashlib.md5(param.encode()).hexdigest()
    stub_md5 = hashlib.md5(data.encode()).hexdigest() if data else "00000000000000000000000000000000"

    gorgon = [int(url_md5[i:i+2], 16) for i in range(0, 8, 2)]
    gorgon += [int(stub_md5[i:i+2], 16) for i in range(0, 8, 2)]
    gorgon += [0, 8, 16, 9]
    gorgon += [int(hex(ttime)[i:i+2], 16) for i in range(2, 10, 2)]

    def reverse(num):
        tmp_string = hex(num)[2:].zfill(2)
        return int(tmp_string[1] + tmp_string[0], 16)

    def rbit(num):
        return int(bin(num)[2:].zfill(8)[::-1], 2)

    def xg_calculate(debug):
        for i in range(len(debug)):
            A = debug[i]
            B = reverse(A)
            C = debug[(i + 1) % len(debug)]
            D = B ^ C
            E = rbit(D)
            F = E ^ len(debug)
            debug[i] = int(hex(~F & 0xFF)[-2:], 16)
        return debug

    xg_hash = ''.join(hex(x)[2:].zfill(2) for x in xg_calculate(gorgon))

    return {"X-Gorgon": "8402" + xg_hash, "X-Khronos": str(ttime)}

def get_profile(session_id, device_id, iid):
    try:
        params = f"device_id={device_id}&iid={iid}&version_code=34.0.0"
        sig = getxg(params, "")
        headers = {
            "Cookie": f"sessionid={session_id}",
            "X-Gorgon": sig["X-Gorgon"],
            "X-Khronos": sig["X-Khronos"],
        }
        url = f"https://api16.tiktokv.com/aweme/v1/user/profile/self/?{params}"
        response = requests.get(url, headers=headers)
        return response.json()["user"]["unique_id"]
    except Exception:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session_id = request.form['session_id']
        new_username = request.form['new_username']
        device_id = str(random.randint(777777788, 999999999999))
        iid = str(random.randint(777777788, 999999999999))

        current_user = get_profile(session_id, device_id, iid)
        if current_user:
            data = f"unique_id={quote(new_username)}"
            params = f"device_id={device_id}&iid={iid}&version_code=34.0.0"
            sig = getxg(params, data)
            headers = {
                "Cookie": f"sessionid={session_id}",
                "X-Gorgon": sig["X-Gorgon"],
                "X-Khronos": sig["X-Khronos"],
            }
            url = f"https://api16.tiktokv.com/aweme/v1/commit/user/?{params}"
            response = requests.post(url, data=data, headers=headers)
            if "unique_id" in response.text:
                return f"Username successfully changed to {new_username}"
            else:
                return "Failed to change username."
        return "Invalid session ID or other error."
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
