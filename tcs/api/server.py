import asyncio
from threading import Thread
from flask import Flask, abort, request, jsonify
from tcs.cache.cache import FrameCache
from tcs.tcp.socket import SocketInterface


app = Flask(__name__)

@app.route('/v1/register', methods=['POST'])
def register() -> str:
    payload: dict = request.json
    apr = payload.get('apr')
    if apr is None:
        abort(400)
    with FrameCache() as fc:
        result = fc.get(apr)
    if not result:
        abort(401)
    # TODO: run random port selection on set of available ports
    port = 5000
    # start new socket connection
    socket = SocketInterface(addr="localhost:{}".format(port))
    Thread(name=apr, target=socket.run, args=(), daemon=True).start()
    payload = {
        'port': port
    }
    return jsonify(payload)
