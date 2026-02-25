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
        # Ensure timeout so the app doesn't hang if Redis is slow
        g.redis = Redis(host="redis", port=6379, db=0, socket_timeout=5)
    return g.redis

@app.route("/", methods=['POST','GET'])
def hello():
    voter_id = request.cookies.get('voter_id')
    if not voter_id:
        # uuid is now imported at the top to prevent Gunicorn boot errors
        voter_id = hex(uuid.getnode())

    vote = None

    if request.method == 'POST':
        try:
            redis = get_redis()
            # .values.get is more robust for NGINX Ingress data
            vote = request.values.get('vote')
            if vote:
                app.logger.info(f"Received vote for {vote}")
                data = json.dumps({'voter_id': voter_id, 'vote': vote})
                redis.rpush('votes', data)
            else:
                app.logger.warning("POST received but 'vote' data was empty")
        except Exception as e:
            app.logger.error(f"Error connecting to Redis: {e}")

    resp = make_response(render_template(
        'index.html',
        option_a=option_a,
        option_b=option_b,
        hostname=hostname,
        vote=vote,
    ))
    
    # Set cookie to keep track of the user session
    resp.set_cookie('voter_id', voter_id)
    return resp

if __name__ == "__main__":
    # Standard Flask dev server (only used if running app.py directly)
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
