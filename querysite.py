import concurrent.futures
import socket

import flask
import valve.source.a2s
import valve.source.messages

def yesno(value):
    if value:
        return "Yes"
    else:
        return "No"

def format_duration(total_seconds):
    total_seconds = int(total_seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return "{}h {}m".format(hours, minutes)
    elif minutes > 0:
        return "{}m {}s".format(minutes, seconds)
    else:
        return "{}s".format(seconds)

app = flask.Flask(__name__)

@app.route("/")
def redirect_index():
    return flask.redirect("/query")

@app.route("/query")
def query():
    server_arg = flask.request.args.get("server", default=None)
    server_arg = server_arg.strip()
    if not server_arg:
        return flask.render_template("query.html", status="Empty")
    if ":" in server_arg:
        ip, port_str = server_arg.split(":", 1)
    elif " " in server_arg:
        ip, port_str = server_arg.split(None, 1) # Split on whitespace
    else:
        return flask.render_template("query.html", status="Error",
            error="Port is missing."), 400
    
    try:
        port = int(port_str)
    except ValueError:
        return flask.render_template("query.html", status="Error",
            error="Port is not a number."), 400
    if not 0 < port < 65536:
        return flask.render_template("query.html", status="Error",
            error="Port has to be between 0 and 65535."), 400

    try:
        socket.getaddrinfo(ip, port_str)
    except socket.gaierror:
        return flask.render_template("query.html", status="Error",
            error="Invalid server address."), 400

    # We need 2 queriers because requests are not thread safe
    info_querier = valve.source.a2s.ServerQuerier((ip, port), timeout=3)
    players_querier = valve.source.a2s.ServerQuerier((ip, port), timeout=3)
    with concurrent.futures.ThreadPoolExecutor() as pool:
        info_future = pool.submit(info_querier.info)
        players_future = pool.submit(players_querier.players)
    concurrent.futures.wait((info_future, players_future))
    
    server_exception = info_future.exception() or players_future.exception()
    if type(server_exception) == valve.source.a2s.NoResponseError:
        return flask.render_template("query.html", status="Error",
            error="Server did not respond."), 200
    if type(server_exception) == valve.source.messages.BrokenMessageError:
        return flask.render_template("query.html", status="Error",
            error="Server sent a broken response."), 200
    elif server_exception is not None:
        raise server_exception
    
    info_res = info_future.result()
    players_res = players_future.result()
        
    info = dict(info_res)
    info["password_protected"] = yesno(info_res["password_protected"])
    info["vac_enabled"] = yesno(info_res["vac_enabled"])
    
    players = []
    for player_entry in players_res["players"]:
        player = dict(player_entry)
        player["duration"] = format_duration(player_entry["duration"])
        players.append(player)
    players.sort(key=lambda p: p["score"], reverse=True)
    
    return flask.render_template("query.html", status="Success", 
        info=info, players=players)

@app.errorhandler(500)
def server_error(e):
    return flask.render_template("error.html", status="Error",
        error="An unexpected error occured."), 500

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5001)
