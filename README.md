# Self host fonts

A very simple python script that makes self hosting (google) fonts easy

# Requirements

- python 3.6+

# Installation

- clone this repo
- run `pip install -r requirements.txt`

# Usage

`python run.py [url] [-d Directory] [-s] [-p prefix] [-f stylesheet-name] [--ua user-agent]`

# Options

Any google font configuration is supported as long as you provide the correct url

- `-d` the directory where your woff files are stored (defaults to `fonts/`)
- `-s` if should force `font-display:swap` (defaults to `False`)
- `-p` folder prefix for your woff files (defaults to `./`)
- `-f` stylesheet name (defaults to `stylesheet.css`)
- `--ua` the user agent (defaults to chrome 88) (your user agent string determines which font formats google will serve)
