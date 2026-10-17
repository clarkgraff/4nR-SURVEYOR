"""D7 human-curated shared discovery catalogue; never claims factual verification."""
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from .vetting import AuditLog
from .specialists import SPECIALISTS

class KnowledgeCatalogue:
    def __init__(self, database):
        self.connection=sqlite3.connect(str(database))
        self.connection.row_factory=sqlite3.Row
        self.connection.execute("""CREATE TABLE IF NOT EXISTS knowledge (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          suite TEXT NOT NULL, title TEXT NOT NULL, url TEXT NOT NULL,
          provider TEXT NOT NULL, presentation_id TEXT NOT NULL,
          source_index INTEGER NOT NULL, operator TEXT NOT NULL,
          rationale TEXT NOT NULL, status TEXT NOT NULL, created_utc TEXT NOT NULL,
          UNIQUE(presentation_id, source_index))""")
        self.connection.commit()

    def add(self,presentation_file,item,archive):
        report=json.loads(Path(presentation_file).read_text(encoding="utf-8-sig"))
        if report.get("schema")!="surveyor.presentation.v0" or report.get("suite") not in SPECIALISTS:
            raise ValueError("Invalid presentation")
        if not isinstance(item,int) or not 1<=item<=len(report["sources"]):
            raise ValueError("Invalid source index")
        source=report["sources"][item-1]
        log=AuditLog(Path(archive)/"presentation-decisions.jsonl")
        log.validate()
        events=[json.loads(line)["event"] for line in log.path.read_text(encoding="utf-8").splitlines()] if log.path.exists() else []
        decisions=[e for e in events if e.get("schema")=="surveyor.user-disposition.v0"
                   and e.get("presentation_id")==report["presentation_id"]
                   and e.get("source_index")==item and e.get("source_url")==source["url"]]
        if not decisions or decisions[-1]["action"]!="approve":
            raise ValueError("Latest operator decision must approve discovery candidate")
        decision=decisions[-1]
        now=datetime.now(timezone.utc).isoformat()
        self.connection.execute("INSERT OR IGNORE INTO knowledge(suite,title,url,provider,presentation_id,source_index,operator,rationale,status,created_utc) VALUES(?,?,?,?,?,?,?,?,?,?)",
           (report["suite"],source["title"],source["url"],source["provider"],
            report["presentation_id"],item,decision["operator"],decision["rationale"],
            "curated_candidate_unverified",now))
        self.connection.commit()
        record=self.connection.execute("SELECT * FROM knowledge WHERE presentation_id=? AND source_index=?",
                                       (report["presentation_id"],item)).fetchone()
        return dict(record)

    def search(self,term,limit=25):
        if not isinstance(term,str) or not term.strip() or not 1<=limit<=100:
            raise ValueError("Invalid search")
        escaped=term.replace("\\","\\\\").replace("%","\\%").replace("_","\\_")
        rows=self.connection.execute("SELECT * FROM knowledge WHERE title LIKE ? ESCAPE '\\' OR url LIKE ? ESCAPE '\\' ORDER BY id DESC LIMIT ?",
                                     ("%"+escaped+"%","%"+escaped+"%",limit)).fetchall()
        return [dict(row) for row in rows]

    def close(self):self.connection.close()
