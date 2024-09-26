# %%
from pathlib import Path
import json
import copy
from collections import defaultdict
from shutil import copyfile

from dotenv import load_dotenv

load_dotenv(override=True)

from fdllm import get_caller
from fdllm.extensions import general_query
from tqdm import tqdm

from constants import ROOT

# %%
lpjson = ROOT / r"mbsseKP_files_lessonplans_parsed.json"
with open(lpjson) as f:
    lpdict = json.load(f)

lpjson_clean = lpjson.parent / "mbsseKP_files_lessonplans_parsed_cleaned.json"
if lpjson_clean.exists():
    with open(lpjson_clean) as f:
        lpclean = json.load(f)
else:
    lpclean = copy.deepcopy(lpdict)
    for file in lpclean:
        for plan in file["plans"]:
            plan["Body"] = None
    with open(lpjson_clean, "w") as f:
        json.dump(lpclean, f, indent=4)
# %%
caller = get_caller("gpt-4o-2024-08-06")


# %%
def gen_jsonin(lp):
    return {"text": lp["Body"]}


def gen_jsonout(lp):
    return {
        (
            "markdown"
            ":: Format the text into markdown "
            "using headings, lists, tables where appropriate."
            " Convert unicode to ascii where possible."
            " Use latex for mathematical formulas."
            " Remove any duration information."
            " Remove any whitespace from inside words."
            # " Extract any extra material in 'Closing',"
            # " under the heading [...], and insert it into"
            # " 'Teaching Aids' as a list of heading: text pairs."
        ): {key: None for key in lp["Body"]},
        ("duration:: extract duration from text if applicable to here"): {
            key: None for key in lp["Body"]
        },
        (
            "extra:: Any material under the heading [...]"
            " and/or any material referenced in 'Teaching Aids'"
        ): [{"heading": None, "markdown": None}],
    }

for i, file in tqdm(enumerate(lpdict), total=len(lpdict)):
    for j, plan in enumerate(file["plans"]):
        bak = lpjson_clean.with_suffix(".bak")
        copyfile(lpjson_clean, bak)
        with open(lpjson_clean) as f:
            lpclean = json.load(f)
        if lpclean[i]["plans"][j]["Lesson Title"] != plan["Lesson Title"]:
            raise ValueError("lpclean is misformatted")
        if lpclean[i]["plans"][j]["Body"] is not None:
            continue
        try:
            out = general_query(gen_jsonin(plan), gen_jsonout(plan), caller=caller)
            out2 = defaultdict(dict)
            for key1, val1 in out.items():
                if key1 != "extra":
                    for key2, val2 in val1.items():
                        out2[key2][key1] = val2
            lpclean[i]["plans"][j]["Body"] = out2
            lpclean[i]["plans"][j]["extra"] = out["extra"]
        except:
            lpclean[i]["plans"][j]["Body"] = ""
            lpclean[i]["plans"][j]["extra"] = None
        with open(lpjson_clean, "w") as f:
            json.dump(lpclean, f, indent=4)


# #%%
# for fld, val in clean_keys(out[0])["markdown"].items():
#     with open(f"{fld}.md", "w") as f:
#         f.write(val)
