import io
import json
import zipfile
from logger import info as l, error
from json import JSONDecodeError

from PIL import Image

from func import get_texture_id, to_BG


def parse_info_txt(content: str):
    content = content.strip().strip("#").split("\r\n")
    content = [x.split(": ") for x in content]
    result = {}
    for i in content:
        if len(i) == 2:
            result[i[0]] = i[1].strip()
    return result

def parse_csv(content: str):
    content = content.strip().split("\r\n")
    keys = content[0].split(',')
    values = content[1].split(',')
    result = {}
    for i in range(len(keys)):
        try:
            if not ((values[i].startswith('"') and values[i].endswith('"'))\
                    or (values[i].startswith("'") and values[i].endswith("'"))):
                result[keys[i]] = values[i]
            else:
                result[keys[i]] = values[i][1:-1]
        except IndexError:
            result[keys[i]] = ''
    return result


def parse_chart(chart_path: str):
    l("Loading Chart...")
    result = {"JudgeLineTexture": {}}
    if zipfile.is_zipfile(chart_path):
        with zipfile.ZipFile(chart_path, "r") as file:
            result["isZip"] = True
            filenames = file.namelist()
            for name in filenames:
                if name.startswith("info"):
                    if name.endswith(".txt"):
                        info = parse_info_txt(file.read(name).decode())
                        result["Name"] = info["Name"]
                        result["Audio"] = file.read(info["Song"])
                        BG = io.BytesIO(file.read(info["Picture"]))
                        with Image.open(BG) as img:
                            result["BG"] = get_texture_id(to_BG(img))
                        result["Chart"] = json.loads(file.read(info["Chart"]).decode())
                        result["Level"] = info["Level"]
                        result["Charter"] = info["Charter"]
                        result["Composer"] = info["Composer"]
                    if name.endswith(".csv"):
                        print(file.read(name).decode())
                        info = parse_csv(file.read(name).decode())
                        result["Name"] = info["Name"]
                        result["Audio"] = file.read(info["Music"])
                        BG = io.BytesIO(file.read(info["Image"]))
                        with Image.open(BG) as img:
                            result["BG"] = get_texture_id(to_BG(img))
                        result["Chart"] = json.loads(file.read(info["Chart"]).decode())
                        result["Level"] = info["Level"]
                        result["Charter"] = info["Charter"]
                        result["Composer"] = info["Artist"]
            if "formatVersion" not in info["Chart"]:
                for line in result["Chart"]["judgeLineList"]:
                    if "Texture" in line:
                        if line["Texture"] != "line.png" and line["Texture"] not in result["JudgeLineTexture"]:
                            l(f"Loading texture: {line['Texture']}")
                            texture = io.BytesIO(file.read(line["Texture"]))
                            result["JudgeLineTexture"][line["Texture"]] = get_texture_id(Image.open(texture))
    else:
        result["isZip"] = False
        try:
            with open(chart_path, "r", encoding="utf-8") as f:
                result["Chart"] = json.load(f)
        except JSONDecodeError:
            result["err"] = "Not a JSON"
    if "formatVersion" in result["Chart"]:
        l("Success")
        l(f"fmt={result['Chart']['formatVersion']}")
    elif "META" in result["Chart"]:
        l("Success")
        l(f"fmt=RPE{result['Chart']['META']['RPEVersion']}")
    else:
        error("unknown fmt")
        raise "未知格式"
    return result

