# Source Server Query

Website for querying servers that support the [A2S] protocol.

## Supported Games

Alien Swarm, Empires, Fistful of Frags, Garry's Mod, Half Life, Half Life 2, Just Cause 2, Left 4 Dead, Rust, Synergy, Team Fortress Classic, Team Fortress 2, ...

## Runing locally

Run the script with `python3 querysite.py` and open [http://localhost:5001](http://localhost:5001) in your browser.

## Deployment

Check out the flask manual about [Deployment Options]. An example uwsgi configuration is provided in `/uwsgi`.

## Dependencies

* [python-valve]
* [flask]

## License

AGPLv3

[A2S]: https://developer.valvesoftware.com/wiki/Server_queries
[python-valve]: https://github.com/Holiverh/python-valve
[flask]: http://flask.pocoo.org/
[Deployment Options]: http://flask.pocoo.org/docs/latest/deploying/
