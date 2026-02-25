@app.route("/", methods=['POST','GET'])
def hello():
    voter_id = request.cookies.get('voter_id')
    if not voter_id:
        voter_id = hex(uuid.getnode())

    vote = None

    if request.method == 'POST':
        redis = get_redis()
        # Use .get() to prevent the KeyError crash
        vote = request.form.get('vote')
        if vote:
            data = json.dumps({'voter_id': voter_id, 'vote': vote})
            redis.rpush('votes', data)

    resp = make_response(render_template(
        'index.html',
        option_a=option_a,
        option_b=option_b,
        hostname=hostname,
        vote=vote,
    ))
    resp.set_cookie('voter_id', voter_id)
    return resp
