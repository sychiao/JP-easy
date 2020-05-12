from pyknp import KNP
from typing import List
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re


knp = KNP()     # Default is JUMAN++. If you use JUMAN, use KNP(jumanpp=False)

def is_kana(char):
    return ord("\u30A2") <= ord(char) <= ord("\u30FA") or ord("\u3041") <= ord(char) <= ord("\u3096")

def toruby(midasi: str, yomi: str):
    lst = list()
    word_table = dict()
    TOK = True
    no_kanna = True
    for char in midasi:
        if is_kana(char) or char == "。":
            lst.append(char)
            TOK = True
            no_kanna = False
        else:
            if TOK:
                lst.append("$TOK")
                TOK = False
    if no_kanna:
        return f"<ruby>{midasi}<rt>{yomi}</rt><ruby>"
    else:
        match_ruby = re.match("".join(lst).replace("$TOK",(r"(.*?)")), yomi)
        match_word = re.match("".join(lst).replace("$TOK",(r"(.*?)")), midasi)
        text = "".join(lst)
        for word, ruby in zip(match_word.groups(), match_ruby.groups()):
            ruby = f"<ruby>{word}<rt>{ruby}</rt><ruby>"
            text = text.replace("$TOK", ruby, 1)
        return text

text = "太郎はこの本を二郎を見た女性に渡した。\n下鴨神社の参道は暗かった。"

def parse_sent(sent: str):
    result = knp.parse(sent)
    lst=list()
    for bnst in result.bnst_list():
        #print(f"id:{bnst.bnst_id} link:{bnst.parent_id} {''.join(mrph.midasi for mrph in bnst.mrph_list())}")
        retidct = {"id": bnst.bnst_id, "link":bnst.parent_id, 
        "mrph":[toruby(mrph.midasi, mrph.yomi) for mrph in bnst.mrph_list()]}
        lst.append(retidct)
    return lst

def parse_text(text: str):
    text = text.replace(" ","")
    text = text.replace("\n","。")
    textlst = [sent+"。" for sent in text.split("。") if len(sent) != 0]
    return [parse_sent(sent) for sent in textlst]
        
#print(parse_text(text))

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    message: str

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/")
async def post(raw_str: Item):
    return parse_text(raw_str.message)

#print("".join(["".join(e["mrph"]) for e in lst]))

#print(toruby("この本を見た", "このほんをみた"))

'''
print("文節")
for bnst in result.bnst_list():
    print("\tID:%d, 見出し:%s, 係り受けタイプ:%s, 親文節ID:%d, 素性:%s" \
            % (bnst.bnst_id, "".join(mrph.midasi for mrph in bnst.mrph_list()), bnst.dpndtype, bnst.parent_id, bnst.fstring))

print("\n基本句")
for tag in result.tag_list(): # 各基本句へのアクセス
    print("\tID:%d, 見出し:%s, 係り受けタイプ:%s, 親基本句ID:%d, 素性:%s" \
            % (tag.tag_id, "".join(mrph.midasi for mrph in tag.mrph_list()), tag.dpndtype, tag.parent_id, tag.fstring))

print("形態素")
for mrph in result.mrph_list(): # 各形態素へのアクセス
    print(f"\tID{mrph.mrph_id}")
    print("\tID:%d, 見出し:%s, 読み:%s, 原形:%s, 品詞:%s, 品詞細分類:%s, 活用型:%s, 活用形:%s, 意味情報:%s, 代表表記:%s" \
            % (mrph.mrph_id, mrph.midasi, mrph.yomi, mrph.genkei, mrph.hinsi, mrph.bunrui, mrph.katuyou1, mrph.katuyou2, mrph.imis, mrph.repname))
'''
