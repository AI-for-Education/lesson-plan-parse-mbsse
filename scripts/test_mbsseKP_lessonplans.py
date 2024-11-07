# %%
import json
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

from parsefuns_MBSSE import (
    parse_lp_tryer,
    format_lesson_number,
    clean_strings,
    fix_title,
    lpgen,
)
from download_MBSSE import download_MBSSE
from formats_MBSSE import USEKEYS
from constants import ROOT

# %%
lp_file = ROOT / "mbsseKP_files_lessonplans_parsed_cleaned.json"
if not lp_file.exists():
    download_MBSSE(out_file=lp_file)

with open(lp_file) as f:
    jsondata_lessonplan = json.load(f)