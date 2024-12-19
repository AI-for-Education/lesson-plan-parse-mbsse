# %%
import json
from collections import defaultdict
from pathlib import Path
import subprocess
from itertools import chain
import re

import pandas as pd
from tqdm import tqdm
from nltk.corpus import wordnet as wn

from download_MBSSE import download_MBSSE
from constants import ROOT

lp_file = ROOT / "mbsseKP_files_lessonplans_parsed_cleaned.json"
if not lp_file.exists():
    download_MBSSE(out_file=lp_file)


def load_mbsse_extras(lp_file=lp_file):
    # load extras for GPF grades: primary 1-6, JSS 1-3
    with open(lp_file, "r") as f:
        mbsse = json.load(f)

    extras = []
    for file in mbsse:
        # only want GPF grades 1-9 so can skip SSS
        level = file["file_meta"]["Level"]
        subject = file["file_meta"]["Subject"]
        if level == "sss":
            continue
        if subject == "mathematics":
            continue

        for plan in file["plans"]:
            if plan["extra"]:
                for extra in plan["extra"]:
                    if extra["markdown"]:
                        if "Part" in file["file_meta"]:
                            file_meta = {
                                "part": file["file_meta"]["Part"],
                            }
                        else:
                            file_meta = {
                                "year": file["file_meta"]["Year"],
                                "term": file["file_meta"]["Term"],
                            }
                        file_meta["level"] = level
                        file_meta["subject"] = subject

                        if level == "primary":
                            file_meta["gpf_grade"] = file_meta["year"]
                        elif level == "jss":
                            file_meta["gpf_grade"] = file_meta["year"] + 6

                        extras.append(
                            {
                                **extra,
                                **file_meta,
                                "class_level": plan["Class/Level"],
                                "theme": plan["Theme"],
                                "lesson_title": plan["Lesson Title"],
                                "lesson_number": plan["Lesson Number"],
                                "filename": file["filename"],
                            }
                        )

    # add an arbitrary ID number based on load order
    for i, x in enumerate(extras):
        x["id"] = i
    return extras

def sort_counter(counter):
    return dict(sorted(counter.items(), key=lambda x: x[1], reverse=True))

# %%
## prepare exras for export

# load in extras from lesson plans
extras = load_mbsse_extras()

# dataframes
dfs = {}
# markdown texts
mds = {}

for grade in range(1, 10):
    extras_grade = [x for i, x in enumerate(extras) if x["gpf_grade"] == grade]

    # Excel table from pandas df
    data = defaultdict(list)
    cols = ["id", "heading", "markdown", "gpf_grade"]
    for col in cols:
        data[col] = [x[col] for x in extras_grade]
    df = pd.DataFrame(data)
    dfs[grade] = df

    # Format a document
    md = ""
    for x in extras_grade:
        md += f"**Item: {x['id']}, Grade: {x['gpf_grade']}**\n\n"
        md += f"Heading: {x['heading']}\n\n"
        md += x["markdown"]
        md  += "\n\n\n"
    mds[grade] = md

# %%
### simple word count

with open(lp_file) as f:
    lpcleaned = json.load(f)

levels = ["primary", "jss", "sss"]

lp_materials = defaultdict(list)
for doc in lpcleaned:
    for level in levels:
        if (
            doc["file_meta"]["Subject"] in ["language-arts", "english-language"]
            and doc["file_meta"]["Level"].lower() == level
        ):
            for plan in doc.get("plans", []):
                extralist = plan.get("extra", [])
                if extralist is not None:
                    for ex in extralist:
                        extratxt = ex.get("markdown")
                        if extratxt is not None and extratxt != "None":
                            lp_materials[level].append({"text": extratxt})


word_counter = defaultdict(lambda: defaultdict(lambda: 0))

# for fileobj in tqdm(
#     chain(jsondata_general, jsondata_lessonplan),
#     total=len(jsondata_general) + len(jsondata_lessonplan),
# ):
for level in levels:
    for fileobj in tqdm(lp_materials[level]):
        words = re.sub(r"[^A-Za-z -]", "", fileobj["text"]).split()
        for word in words:
            if all(c != "-" for c in word):
                word_counter[level][word] += 1

word_counter = {level: sort_counter(word_counter[level]) for level in levels}

word_counter_ignore_case = defaultdict(lambda: defaultdict(lambda: 0))
for level in levels:
    for word, count in word_counter[level].items():
        word_counter_ignore_case[level][word.lower()] += count

word_counter_ignore_case = {
    level: sort_counter(word_counter_ignore_case[level]) for level in levels
}

### ignore case
max_print = 100
for level in levels:
    for i, (w, c) in enumerate(word_counter_ignore_case[level].items()):
        print(f"{level} -- {w}: {c}")
        if i > max_print:
            break

print()

### save lists
outseries_dict = {
    level: pd.Series(word_counter_ignore_case[level], name="word_count")
    for level in levels
}

for level, sr in outseries_dict.items():
    sr.to_csv(ROOT / f"frequent_words_{level}.csv")
