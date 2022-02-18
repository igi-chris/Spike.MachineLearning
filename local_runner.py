"""
Runs a local web server to expose the file transformation service.
Can be used to integrate with other applications e.g. p:IGI+ without 
the need to send data over the internet.
"""
from argparse import ArgumentParser

from app import app as flask_app


DEFAULT_PORT = 5000


def run(port: int=DEFAULT_PORT):
    flask_app.run(port=port)


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('-p', '--port', dest='port', type=int, 
                        default=DEFAULT_PORT, required=False,
                        help="The port to use for the local web service.")
    args = parser.parse_args()

    try:
        from waitress import serve
        # start with waitress (prod wsgi http server)
        serve(flask_app, host='127.0.0.1', port=args.port, threads=2)
    except ModuleNotFoundError:
        run(args.port)  # start with built-in flask wsgi server (for dev/debug)
