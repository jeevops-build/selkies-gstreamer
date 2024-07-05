# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from flask import Flask, request
import os, time, hmac, hashlib, base64, json
app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def turn_rest():
    service_input = request.values.get('service') or 'turn'
    if service_input:
        service_input = service_input.lower()

    shared_secret = os.environ.get('TURN_SHARED_SECRET', 'openrelayprojectsecret')
    turn_host = os.environ.get('TURN_HOST', 'staticauth.openrelay.metered.ca')
    if turn_host:
        turn_host = turn_host.lower()
    turn_port = os.environ.get('TURN_PORT', '443')
    if not turn_port.isdigit():
        turn_port = '3478'
    username_input = request.values.get('username') or request.headers.get('x-auth-user') or request.headers.get('x-turn-username') or 'turn-rest'
    if username_input:
        username_input = username_input.lower()
    protocol = request.values.get('protocol') or request.headers.get('x-turn-protocol') or os.environ.get('TURN_PROTOCOL', 'udp')
    if protocol.lower() != 'tcp':
        protocol = 'udp'
    turn_tls = request.values.get('tls') or request.headers.get('x-turn-tls') or os.environ.get('TURN_TLS', 'false')
    if turn_tls.lower() == 'true':
        turn_tls = True
    else:
        turn_tls = False

    # Sanitize user for credential compatibility
    user = username_input.replace(":", "-")

    # Credential expires in 24 hours
    expiry_hour = 24

    exp = int(time.time()) + expiry_hour * 3600
    username = "{}:{}".format(exp, user)

    # Generate HMAC credential
    hashed = hmac.new(bytes(shared_secret, "utf-8"), bytes(username, "utf-8"), hashlib.sha1).digest()
    password = base64.b64encode(hashed).decode()

    rtc_config = {}
    rtc_config["lifetimeDuration"] = "{}s".format(expiry_hour * 3600)
    rtc_config["blockStatus"] = "NOT_BLOCKED"
    rtc_config["iceTransportPolicy"] = "all"
    rtc_config["iceServers"] = []
    rtc_config["iceServers"].append({
        "urls": [
            "stun:{}:{}".format(turn_host, turn_port),
            "stun:stun.l.google.com:19302"
        ]
    })
    rtc_config["iceServers"].append({
        "urls": [
            "{}:{}:{}?transport={}".format('turns' if turn_tls else 'turn', turn_host, turn_port, protocol)
        ],
        "username": username,
        "credential": password
    })

    return json.dumps(rtc_config, indent=2)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8008")
