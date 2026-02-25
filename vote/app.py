from flask import Flask, render_template, request, make_response, g
from redis import Redis
import os
import socket
import random
import json
import uuid

# Configuration
option_a = os.getenv('OPTION_A', "Cats")
option_b = os.getenv('OPTION_B', "Dogs")
hostname = socket.gethostname()

app = Flask(__name__)

def get_redis():
    if not hasattr(g, 'redis'):
        # Ensure we use the 'redis' service name defined in K8s
        g.redis = Redis(host="redis", port=6379, db=0, socket_timeout=5)
    return g.redis

@app.route("/", methods=['POST','GET'])
def hello():
    voter_id = request.cookies.get('voter_id')
    if not voter_id:
        voter_id = hex(uuid.getnode())

    vote = None

    if request.method == 'POST':
        try:
            redis = get_redis()
            # Use .get() to avoid KeyError and handle empty data
            vote = request.form.get('vote')
            if vote:
                app.logger.info(f"Received vote for {vote}")
                data = json.dumps({'voter_id': voter_id, 'vote': vote})
                redis.rpush('votes', data)
            else:
                app.logger.warning("POST received but 'vote' field was empty")
        except Exception as e:
            app.logger.error(f"Redis Error: {e}")

    resp = make_response(render_template(
        'index.html',
        option_a=option_a,
        option_b=option_b,
        hostname=hostname,
        vote=vote,
    ))
    
    resp.set_cookie('voter_id', voter_id)
    return resp

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
