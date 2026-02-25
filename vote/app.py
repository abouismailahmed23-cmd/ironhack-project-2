@app.route("/", methods=['POST','GET'])
def hello():
    voter_id = request.cookies.get('voter_id')
    if not voter_id:
        voter_id = hex(uuid.getnode())

    vote = None

    if request.method == 'POST':
        redis = get_redis()
        # Use .values.get to be more flexible with Ingress/Proxy data
        vote = request.values.get('vote') 
        if vote:
            app.logger.info(f"Received vote for {vote}")
            data = json.dumps({'voter_id': voter_id, 'vote': vote})
            redis.rpush('votes', data)
        else:
            app.logger.warning("POST received but NO VOTE DATA found in request")

    # ... rest of your code
