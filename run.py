from argparse import ArgumentParser
from pathlib import Path
from urllib.parse import parse_qs, urlencode
from io import StringIO

import requests
import tinycss2

from URL import URL

DEFAULT_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.11 Safari/537.36"
headers = {"user-agent": DEFAULT_USER_AGENT}


def download_fonts(
    url: str,
    should_swap=True,
    user_agent=DEFAULT_USER_AGENT,
    out_dir=Path("."),
    prefix="./",
    file="stylesheet.css",
):
    headers["user-agent"] = user_agent
    dl = download(url, should_swap)
    create_output(dl, out_dir, prefix, file)


def create_output(text: str, out: Path, prefix: str, file: str):
    output = StringIO()
    css = tinycss2.parse_stylesheet(text)
    for k in css:
        if k.type == "at-rule" and k.at_keyword == "font-face":
            output.write("@font-face{")
            for token in k.content:
                if token.type == "url":
                    url = URL(token.value)
                    name = url.get_suggested_filename()
                    f = out / name
                    print(f"downloading {url} to {f} ")
                    req = url.fetch(headers=headers)
                    f.write_bytes(req.content)
                    output.write(f"url('{prefix}{f}')")
                    continue
                else:
                    output.write(token.serialize())
            output.write("}")
        else:
            output.write(k.serialize())
    output.seek(0)
    Path(file).write_text(output.read())


def download(u, swap) -> str:
    url = URL(u)
    if swap:
        qs = url.query
        url_params = parse_qs(qs)
        for k, v in url_params.items():
            url_params[k] = v[0]

        url_params["display"] = "swap"
        url.change_url_attr("query", urlencode(url_params))
        print("fetching:", url)
    req = url.fetch(headers=headers)
    return req.text


def init():

    parser = ArgumentParser(description="Helper to self host google fonts")
    parser.add_argument("url", metavar="URL", type=str, nargs="+")
    parser.add_argument("--ua", metavar="User Agent", default=DEFAULT_USER_AGENT)
    parser.add_argument("-d", metavar="Output directory", default="fonts")
    parser.add_argument("-s", action="store_true", default=False)
    parser.add_argument("-p", metavar="Prefix", default="./")
    parser.add_argument("-f", metavar="File", default="stylesheet.css")
    args = parser.parse_args()

    out_dir = Path(".") / args.d
    ua = args.ua
    swap = args.s
    prefix = args.p
    file = args.f
    out_dir.mkdir(parents=True, exist_ok=True)

    download_fonts(args.url[0], swap, ua, out_dir, prefix, file)


if __name__ == "__main__":
    init()