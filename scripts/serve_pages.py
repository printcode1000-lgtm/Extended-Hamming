"""Serve the repository beneath /Extended-Hamming/ for GitHub Pages path testing."""
from __future__ import annotations

import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "/Extended-Hamming"


class PagesHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path: str) -> str:
        clean = urlsplit(path).path
        if clean == PREFIX:
            clean = PREFIX + "/"
        if clean.startswith(PREFIX + "/"):
            clean = clean[len(PREFIX):]
        else:
            clean = "/__missing__"
        target = (ROOT / clean.lstrip("/")).resolve()
        if ROOT.resolve() not in target.parents and target != ROOT.resolve():
            return str(ROOT / "__missing__")
        return str(target)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    print(f"Serving {ROOT} at http://127.0.0.1:{args.port}{PREFIX}/")
    ThreadingHTTPServer(("127.0.0.1", args.port), PagesHandler).serve_forever()
