import os
import sys
from urllib.parse import parse_qs

# Add root directory to sys.path so backend module can be imported
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app import app

# WSGI Middleware to restore the true request path passed by Vercel
class VercelPathMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        qs = environ.get("QUERY_STRING", "")
        params = parse_qs(qs, keep_blank_values=True)
        if "__path__" in params and params["__path__"]:
            orig_path = params["__path__"][0]
            if not orig_path.startswith("/"):
                orig_path = "/" + orig_path
            environ["PATH_INFO"] = orig_path
            
            # Clean __path__ out of QUERY_STRING
            del params["__path__"]
            new_parts = []
            for k, vals in params.items():
                for v in vals:
                    new_parts.append(f"{k}={v}")
            environ["QUERY_STRING"] = "&".join(new_parts)

        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathMiddleware(app.wsgi_app)
