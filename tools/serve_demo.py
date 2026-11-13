"""Start the packaged demo on loopback and open it after the listener is ready."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import threading
import webbrowser


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--port",type=int,default=8765)
    parser.add_argument("--no-open",action="store_true")
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]/"dist"
    if not (root/"index.html").is_file():
        parser.error("Build the demo first: python tools/build_web.py")
    try:
        server=ThreadingHTTPServer(("127.0.0.1",args.port),partial(SimpleHTTPRequestHandler,directory=str(root)))
    except OSError as error:
        parser.error("Cannot open the local demo port. Try --port 8766. "+str(error))
    url="http://127.0.0.1:"+str(args.port)
    print("RepairScope: "+url,flush=True)
    print("Keep this window open. Ctrl+C stops the local server.",flush=True)
    if not args.no_open:
        opener=threading.Timer(.3,lambda:webbrowser.open(url))
        opener.daemon=True
        opener.start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__=="__main__":
    main()
