"""
Font utils
"""
from pathlib import Path
from argparse import ArgumentParser
from urllib.parse import parse_qs, urlencode, urljoin
from io import StringIO
import tinycss2

from convert import convert_to_woff
from URL import URL


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    "(KHTML, like Gecko) Chrome/100.0.4896.12 Safari/537.36"
)

headers = {"user-agent": DEFAULT_USER_AGENT}


class FontDownloader:
    """
    Font downloader class
    """

    def __init__(
        self,
        url: str,
        prefix="./",
        css_file="stylesheet.css",
        should_convert=True,
        out_dir=Path("."),
        user_agent=DEFAULT_USER_AGENT,
        should_swap=True,
    ) -> None:
        self.url = url
        self.prefix = prefix
        self.css_file = css_file
        self.should_convert = should_convert
        self.out_dir = out_dir
        self.user_agent = user_agent
        self.should_swap = should_swap
        self.headers = {**headers, "user-agent": user_agent}

    def download_stylesheet(self) -> str:
        """
        Download the styleesheet
        Returns:
            str: contents of the stylesheet
        """
        url = URL(self.url)
        if self.should_swap:
            q_s = url.query
            url_params = parse_qs(q_s)
            for k, _v in url_params.items():
                url_params[k] = _v[0]

            url_params["display"] = "swap"
            url.change_url_attr("query", urlencode(url_params))
            print("fetching:", url)
        req = url.fetch(headers=headers)
        return req.text

    def _handle_url(self, output: StringIO, value: str):
        """
        download woff(2?) file
        """
        url = URL(urljoin(self.url, value))

        name = url.get_suggested_filename()
        f_name = self.out_dir / name
        print(f"downloading {url} to {f_name} ")
        req = url.fetch(headers=headers)
        f_name.write_bytes(req.content)
        output.write(f'url("{self.prefix}{f_name}") format("{f_name.suffix[1:]}")')
        if self.should_convert and f_name.suffix != ".woff":
            print(f"converting {f_name} to woff")
            woff = f_name.parent / (f_name.stem + ".woff")
            woff.write_bytes(convert_to_woff(f_name))
            output.write(f',\n\turl("{self.prefix}{woff}") format("woff")')

    def create_output(self, text: str):
        """create the actual output"""
        output = StringIO()
        css = tinycss2.parse_stylesheet(text)
        for k in css:
            if k.type == "at-rule" and k.at_keyword == "font-face":
                output.write("@font-face {")
                skip_format = False
                for token in k.content:
                    if token.type == "function":
                        if token.name == "format":
                            if skip_format:
                                skip_format = False
                                continue
                        if token.name == "url":
                            skip_format = True
                            arg = token.arguments[0]
                            self._handle_url(output, arg.value)

                    if token.type == "url":
                        self._handle_url(output, token.value)
                        continue

                    else:
                        output.write(token.serialize())
                output.write("}")
            else:
                output.write(k.serialize())
        output.seek(0)
        f_name = Path(self.css_file)
        if f_name.stem == f_name.name:
            f_name = Path(f"{f_name}.css")
        f_name.write_text(output.read())


def init():
    """
    Entry point
    """

    parser = ArgumentParser(description="Helper to self host external css fonts")
    parser.add_argument("url", metavar="URL", type=str, nargs="+")
    parser.add_argument("--ua", metavar="User Agent", default=DEFAULT_USER_AGENT)
    parser.add_argument("-d", metavar="Output directory", default="fonts")
    parser.add_argument("-s", action="store_true", default=False)
    parser.add_argument("-p", metavar="Prefix", default="./")
    parser.add_argument("-f", metavar="File", default="stylesheet.css")
    parser.add_argument("-w", action="store_true", default=True)
    parser.add_argument("-c", default="True")
    args = parser.parse_args()

    out_dir = Path(".") / args.d
    u_a = args.ua
    swap = args.s
    prefix = args.p
    file = args.f
    out_dir.mkdir(parents=True, exist_ok=True)
    downloader = FontDownloader(
        args.url[0], prefix, file, args.c.lower() != "false", out_dir, u_a, swap
    )
    sheet = downloader.download_stylesheet()
    downloader.create_output(sheet)


if __name__ == "__main__":

    init()
