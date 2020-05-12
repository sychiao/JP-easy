import urllib.request
import sys
import time
import pathlib
import subprocess
from bs4 import BeautifulSoup


def dl_from_moegirl(url_tok):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    req = urllib.request.Request(url=f"https://zh.moegirl.org/zh-tw/{url_tok}",headers=headers)
    page = urllib.request.urlopen(req)
    soup = BeautifulSoup(page, 'html.parser')

    lyrics = list()
    for e in soup.find_all('div', {'class':"Lyrics-original"}):
        lyrics.extend(e.find('span').text.split(u'\u3000'))
    return lyrics

class mecab_token:
    def __init__(self, word, pos, class1, class2, class3,typeA,typeB,typeO,read=None,sound=None):
        self.word = word
        self.pos = pos
        self.class1 = class1
        self.class2 = class2
        self.class3 = class3
        self.typeA = typeA
        self.typeB= typeB
        self.type = typeO
        self.read = read
        self.sound = sound
    def is_kana(self):
        return all(is_kana(c) for c in self.word)
    def __repr__(self):
        if all(is_kana(c) for c in self.word):
            return f"{self.word}({self.pos})"
        else:
            return f"{self.word}{{{self.read}}}({self.pos})"
        #品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用型,活用形,原形,読み,発音

def mecab_parse_sent(input_str):
    res = subprocess.run(["mecab"], input=input_str.encode('utf-8'), capture_output=True)
    ret = list()
    for line in res.stdout.decode('utf-8').split("\n"):
        if line.find("\t") != -1:
            #print("DEBUG", line)
            word, pos = line.split("\t")
            tok = mecab_token(word, *pos.split(","))
            ret.append(tok)
    return ret

def is_kana(char):
    return ord("\u30A2") <= ord(char) <= ord("\u30FA") or ord("\u3041") <= ord(char) <= ord("\u3096")

lyrics = dl_from_moegirl("%E6%98%8F%E6%9A%97%E4%B9%8B%E6%98%9F_%E9%81%A5%E8%BF%9C%E4%B9%8B%E6%9C%88")
print(lyrics)
for line in lyrics:
    ret = mecab_parse_sent(line)
    add_ruby = list()
    for tok in ret:
        if tok.pos == "記号" or tok.is_kana() or tok.read is None:
            add_ruby.append(tok.word)
        else:
            #add_ruby.append(f"<ruby>{tok.word}<rp>(</rp><rt>{tok.read}</rt><rp>(</rp></ruby>")
            add_ruby.append(f"{{{tok.word}|{tok.read}}}")
    print("".join(add_ruby),"\n")
#ret = mecab_parse_sent("私は先生です")
#print(ret)
