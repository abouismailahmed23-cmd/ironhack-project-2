@app.route("/", methods=['POST','GET'])
def hello():
    voter_id = request.cookies.get('voter_id')
    if not voter_id:
        voter_id = hex(uuid.getnode())

    vote = None

    if request.method == 'POST':
        try:
            # Safely get the vote from form data
            vote = request.form.get('vote')
            if vote:
                app.logger.info(f"Received vote for {vote}")
                # Ensure redis is defined globally or inside this block
                from redis import Redis
                r = Redis(host="redis", port=6379, db=0)
                data = json.dumps({'voter_id': voter_id, 'vote': vote})
                r.rpush('votes', data)
            else:
                app.logger.warning("POST request received but 'vote' key was missing")
        except Exception as e:
            app.logger.error(f"Database error: {e}")

    resp = make_response(render_template(
        'index.html',
        option_a=option_a,
        option_b=option_b,
        hostname=hostname,
        vote=vote,
    ))
    resp.set_cookie('voter_id', voter_id)
    return resp
