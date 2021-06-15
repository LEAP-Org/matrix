from threading import Thread
from flask import Flask, request, abort, jsonify
from flask.wrappers import Response
from tcs.cache.cache import FrameCache
from tcs.tcp.socket import SocketInterface
from tcs.event.registry import Registry as events

app = Flask(__name__)


@app.route('/v1/register', methods=['GET'])
def register() -> Response:
    apr_key = request.headers['Apr']
    if apr_key is None:
        abort(400)
    with FrameCache() as fc:
        result = fc.get(apr_key)
    if not result:
        abort(401)
    # TODO: run random port selection on set of available ports
    port = 6000
    # start new socket connection
    socket = SocketInterface(addr="localhost:{}".format(port))
    Thread(name=apr_key, target=socket.run, args=(), daemon=True).start()
    payload = {
        'port': port
    }
    return jsonify(payload)


@app.errorhandler(400)
def bad_request(_):
    response = jsonify({'message': 'bad request'})
    response.status_code = 400
    return response


@app.errorhandler(401)
def unauthorized(_):
    response = jsonify({'message': 'unauthorized'})
    response.status_code = 401
    return response
