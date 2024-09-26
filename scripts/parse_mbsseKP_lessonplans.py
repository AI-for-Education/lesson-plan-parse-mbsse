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
lp_file = ROOT / "mbsseKP_files_lessonplans.json"
if not lp_file.exists():
    download_MBSSE(out_file=lp_file)

with open(lp_file) as f:
    jsondata_lessonplan = json.load(f)

# %%
ss = [parse_lp_tryer(lp) for lp in jsondata_lessonplan]

# checks
print()
print(sum([isinstance(ss_, tuple) for ss_ in ss]))
print([ss_[2] for ss_ in ss if isinstance(ss_, tuple)])

print(sum(["FullText" in ss__["Body"] for ss_ in ss for ss__ in ss_["plans"]]))
print(sum(["FullText" not in ss__["Body"] for ss_ in ss for ss__ in ss_["plans"]]))

# %%
format_lesson_number(ss)
clean_strings(ss)

# %%
# fix title formatting using LLM
fix_title(ss)

# %%
# create json of values for filtering
filter_values = []
for plan in lpgen(ss):
    if plan["Type"] == "standard":
        fv = {key: val for key, val in plan.items() if key in USEKEYS}
        filter_values.append(fv)

with open("mbsseKP_filter_values.json", "w") as f:
    json.dump(filter_values, f, indent=4)


# %%
## additional checks

myiter = (
    ss__["Body"]["FullText"]
    for ss_ in ss
    for ss__ in ss_["plans"]
    if "FullText" in ss__["Body"]
)

print(next(myiter))

print(set([ss_["filename"] for ss_ in ss for ss__ in ss_["plans"] if not ss__["Body"]]))

print([ss_["plans"][2] for ss_ in ss if ss_["plans"][0] is None])


# %%
# save

with open("mbsseKP_files_lessonplans_parsed.json", "w", encoding="utf-8") as f:
    json.dump(ss, f, indent=4)