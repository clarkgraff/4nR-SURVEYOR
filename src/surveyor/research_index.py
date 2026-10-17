"""Offline passage extraction and keyword candidate matching. Not fact verification."""
from dataclasses import dataclass,asdict
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
import json,re

class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts=[];self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ("script","style","noscript"):self.skip+=1
        if not self.skip and tag in ("p","h1","h2","h3","li","br","article","section"):self.parts.append("\n")
    def handle_endtag(self,tag):
        if tag in ("script","style","noscript") and self.skip:self.skip-=1
        if not self.skip and tag in ("p","li","section","article"):self.parts.append("\n")
    def handle_data(self,data):
        if not self.skip:self.parts.append(data)

@dataclass(frozen=True)
class Passage:
    passage_id:str
    source_sha256:str
    source_url:str
    ordinal:int
    text:str

def source_text(payload:bytes,media_type:str)->str:
    decoded=payload.decode("utf-8-sig",errors="replace")
    if media_type=="text/plain":return decoded
    if media_type=="text/html":
        parser=VisibleText();parser.feed(decoded);return "".join(parser.parts)
    if media_type=="application/json":
        return json.dumps(json.loads(decoded),ensure_ascii=False,indent=2)
    raise ValueError("Unsupported text index media type")

def passages_from_text(text:str,source_sha256:str,source_url:str,*,max_chars:int=950)->list[Passage]:
    if not 100<=max_chars<=4000:raise ValueError("Invalid passage size")
    paragraphs=[re.sub(r"\s+"," ",p).strip() for p in re.split(r"\n\s*\n+",text)]
    result=[]
    for paragraph in paragraphs:
        for start in range(0,len(paragraph),max_chars):
            part=paragraph[start:start+max_chars]
            if not part:continue
            ordinal=len(result)
            result.append(Passage(f"{source_sha256}:{ordinal}",source_sha256,source_url,ordinal,part))
    return result

def index_acquisition(archive,acquisition)->list[Passage]:
    root=Path(archive)
    payload=(root/(acquisition.sha256_hex+".source")).read_bytes()
    if sha256(payload).hexdigest()!=acquisition.sha256_hex:raise ValueError("Source checksum mismatch")
    passages=passages_from_text(source_text(payload,acquisition.media_type),acquisition.sha256_hex,acquisition.url)
    (root/(acquisition.sha256_hex+".passages.json")).write_text(json.dumps([asdict(p) for p in passages],ensure_ascii=False,indent=2),encoding="utf-8")
    return passages

def candidate_passages(claim:str,passages:list[Passage],*,limit:int=5)->list[dict]:
    """Lexical candidates ONLY; matching words do not prove support."""
    if not 1<=limit<=20:raise ValueError("Invalid limit")
    keywords=set(re.findall(r"\b\w{4,}\b",claim.casefold()))
    found=[]
    for p in passages:
        overlap=len(keywords & set(re.findall(r"\b\w{4,}\b",p.text.casefold())))
        if overlap:found.append({"passage_id":p.passage_id,"source_url":p.source_url,"overlap_tokens":overlap,"text":p.text,"verification_status":"candidate_only"})
    return sorted(found,key=lambda x:(-x["overlap_tokens"],x["passage_id"]))[:limit]
