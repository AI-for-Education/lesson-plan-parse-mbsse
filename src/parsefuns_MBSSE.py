import json
import re
import time

from tqdm import tqdm
import openai
from fdllm import get_caller
from fdllm.llmtypes import LLMMessage
from pydantic import BaseModel

from formats_MBSSE import FORMATS, FORMATS_PT


def fmt_sec(sec, ignoretuple=False):
    if ignoretuple and isinstance(sec, tuple):
        return fmt_sec(sec[0])
    else:
        if isinstance(sec, str):
            return r"\s*".join(sec)
        elif isinstance(sec, list):
            return f'(?:{"|".join(fmt_sec(sec_) for sec_ in sec)})'
        elif isinstance(sec, tuple):
            return "".join([r"\s*".join(sec[0]), sec[1]])


def fmt_sec_key(sec, sections_rename):
    if isinstance(sec, str):
        return sections_rename.get(sec, sec).strip(": ")
    elif isinstance(sec, (list, tuple)):
        return fmt_sec_key(sec[0], sections_rename)


def parse_lp_tryer(lp):
    for i, format in enumerate(FORMATS):
        out = parse_lp(lp, format_idx=i, **format)
        if not isinstance(out, tuple):
            return out
        else:
            print(i)
    return out


def parse_plan_text_tryer(pt):
    for i, format in enumerate(FORMATS_PT):
        out = parse_plan_text(pt, **format)
        if "FullText" not in out:
            return out, i
        else:
            print(f"2::{i}")
    return out, None


def parse_lp(lp, sections, sections_rename, format_idx):
    text = lp["text"]
    *keep, drop = text.split("Appendix")
    if keep:
        text = "".join(keep)
    *keep, drop = text.split("Answer Key")
    if keep:
        text = "".join(keep)
    restr = [
        rf"{fmt_sec(sections[i])}(.+?){fmt_sec(sections[i+1], True)}"
        for i in range(len(sections) - 1)
    ]
    restr_simple = [rf"({fmt_sec(sec)})" for sec in sections]
    restr.append(
        rf"{fmt_sec(sections[-2], True)}.+?"
        rf"{fmt_sec(sections[-1], True)}(.+?)"
        rf"(?:{fmt_sec(sections[0], True)}|\s+$)"
    )
    req = [re.compile(restr_, flags=re.DOTALL) for restr_ in restr]
    req_simple = [re.compile(restr_, flags=re.DOTALL) for restr_ in restr_simple]
    parsed_text = [req_.findall(text) for req_ in req]
    parsed_text_simple = [req_.findall(text) for req_ in req_simple]
    nplans = len(parsed_text[0])
    if nplans == 0:
        print(text)
    if not all(len(pt) == nplans for pt in parsed_text) or nplans == 0:
        print([len(pt) for pt in parsed_text])
        print([len(pt) for pt in parsed_text_simple])
        print(restr)
        return None, text, lp["filename"]
    section_list = []
    for i in range(nplans):
        plan = {}
        body_format = None
        for sec, pt in zip(sections, parsed_text):
            key = fmt_sec_key(sec, sections_rename)
            if isinstance(pt[i], str):
                val = pt[i].strip().strip(":")
            elif isinstance(pt[i], tuple):
                val = " ".join(pt_.strip().strip(":") for pt_ in pt[i])
            if key == "Body":
                plan[key], body_format = parse_plan_text_tryer(val)
            else:
                plan[key] = val
        plan["meta_format"] = format_idx
        plan["body_format"] = body_format
        section_list.append(plan)
    lpstruct = {
        **{key: val for key, val in lp.items() if key not in "text"},
        "file_meta": parse_filename(lp["filename"]),
        "plans": section_list,
    }
    return lpstruct


def parse_plan_text(pt, sections):
    restr = "(.+?)".join(fmt_sec(sec) for sec in sections) + "(.+?)$"
    req = re.compile(restr, flags=re.DOTALL)
    groups = req.findall(pt)
    if groups:
        return {fmt_sec_key(sec, {}): g.strip() for sec, g in zip(sections, groups[0])}
    else:
        return {"FullText": pt}


def parse_filename(fn):
    restr = [
        r"lesson-plans-for-(.+?)-(\d+?)-(.+?)-term-(\d+?).pdf",
        r"lesson-plans-for-(.+?)-(.+?)-revision-part-(\d+?).pdf",
    ]
    req = [re.compile(restr_, flags=re.IGNORECASE) for restr_ in restr]
    for i, req_ in enumerate(req):
        tmp = req_.findall(fn)
        if tmp:
            if i == 0:
                out = {
                    "Type": "standard",
                    "Level": tmp[0][0].lower(),
                    "Subject": tmp[0][2].lower(),
                    "Year": int(tmp[0][1]),
                    "Term": int(tmp[0][3]),
                }
            else:
                out = {
                    "Type": "revision",
                    "Level": tmp[0][0].lower(),
                    "Subject": tmp[0][1].lower(),
                    "Part": int(tmp[0][2]),
                }
            return out
    return {"Type": None}


def lpgen(lp):
    for fl in lp:
        for plan in fl["plans"]:
            if plan["body_format"] is not None:
                yield {**plan, **fl["file_meta"]}


def batchgen(myiter, maxn):
    holder = []
    for i, val in enumerate(myiter):
        holder.append(val)
        if (i + 1) % maxn == 0:
            out = holder
            holder = []
            yield out
    yield holder


def fix_title(lp):
    class TitleList(BaseModel):
        titles: list[str]

    # rng = np.random.default_rng(9723537)
    caller = get_caller("gpt-4o-mini-2024-07-18")
    ctx = (
        "Following is a list of titles. Some of the items in the list contain unwanted"
        " whitespace."
        "\n\nReturn a json list with the titles corrected to remove unwanted whitespace"
        " if it appears."
        "\nThe list should be in the same order as the input."
        "\nOnly return the raw json, nothing else."
        "\n\n{}"
    )
    titles = [p["Lesson Title"] for p in lpgen(lp)]
    # rng.shuffle(titles)
    newtitles = []
    maxn = 40
    for batch in tqdm(batchgen(titles, maxn), total=len(titles) // maxn):
        message = LLMMessage(Role="user", Message=ctx.format(json.dumps(batch)))
        out = caller.call(
            message,
            max_tokens=caller.Token_Window - len(caller.tokenize([message])) - 200,
            temperature=0,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "myschema",
                    "strict": True,
                    "schema": {
                        **TitleList.model_json_schema(),
                        "additionalProperties": False,
                    },
                },
            },
        )
        try:
            newlist = json.loads(out.Message)
        except:
            print(out.Message)
            return
        print(json.dumps(newlist, indent=4))
        newtitles.extend(newlist["titles"])
    for ss_ in lp:
        for plan in ss_["plans"]:
            if plan["body_format"] is not None:
                idx = titles.index(plan["Lesson Title"])
                plan["Lesson Title"] = newtitles[idx]


def format_lesson_number(lp):
    for ss_ in lp:
        for p in ss_["plans"]:
            p["Lesson Number"] = int(p["Lesson Number"][-3:])


def clean_strings(lp):
    clean_keys = ["Lesson Title", "Theme"]
    for ss_ in lp:
        for p in ss_["plans"]:
            for key in clean_keys:
                p[key] = p[key].replace("\n", "")


def insert_meta_embeddings(lp):
    client = openai.Client()

    def emb(text, wait=1, cnt=0):
        if cnt > 5:
            raise
        try:
            out = client.embeddings.create(input=text, model="text-embedding-ada-002")
            return out["data"][0]["embedding"]
        except:
            time.sleep(wait)
            return emb(text, wait * 2, cnt + 1)

    def insert(indict):
        for fld in fields:
            if fld not in indict:
                continue
            text = indict[fld]
            response = emb(text)
            indict[f"{fld}_embedding"] = response

    fields = ["Theme", "Subject"]
    for lp_ in tqdm(lp):
        insert(lp_["file_meta"])
        for p in lp_["plans"]:
            insert(p)
