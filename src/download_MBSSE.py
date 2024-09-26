import requests
from pathlib import Path
import gzip
from io import BytesIO
import json

import yaml

from .constants import CFG_PATH, OUT_FILE


def download_MBSSE(cfg_path=CFG_PATH, out_file=OUT_FILE):

    with open(cfg_path) as f:
        cfg = yaml.safe_load(f)

    try:
        response = requests.get(cfg["lp_path"])
    except:
        raise requests.HTTPError()

    if response.status_code == 200:
        content = BytesIO(response.content)

        with gzip.open(content, mode="rb") as zip:
            content_json = json.load(zip)
            with open(out_file, "w") as f:
                json.dump(content_json, f, indent=4)
    else:
        raise requests.HTTPError(f"status code: {response.status_code}")
