"""D8 local Tkinter review interface for archived SURVEYOR presentations.

Only local files, no remote listeners, email, shell execution or implicit web access.
"""
from __future__ import annotations
import json
from pathlib import Path
from .presentation import record_decision
from .knowledge import KnowledgeCatalogue

def launch_gui(archive="surveyor-archive", db="surveyor-knowledge.sqlite3"):
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox, filedialog
    except ImportError as exc:
        raise RuntimeError("Tkinter is required for the local SURVEYOR interface") from exc

    root=tk.Tk()
    root.title("4nR-SURVEYOR — Research Review")
    root.geometry("1060x720")
    archive=Path(archive)
    catalogue=KnowledgeCatalogue(db)
    docs=[]
    current={"path":None,"report":None}
    layout=ttk.Frame(root,padding=12)
    layout.pack(fill="both",expand=True)
    ttk.Label(layout,text="4nR-SURVEYOR | Local Research Review",font=("Segoe UI",16,"bold")).pack(anchor="w")
    ttk.Label(layout,text="Discovery links are NOT verified evidence. Approval means curate a candidate, not certify its accuracy.").pack(anchor="w")
    middle=ttk.Panedwindow(layout,orient="horizontal")
    middle.pack(fill="both",expand=True,pady=8)
    left=ttk.Frame(middle)
    right=ttk.Frame(middle)
    middle.add(left,weight=1)
    middle.add(right,weight=4)
    ttk.Label(left,text="Archived presentations").pack(anchor="w")
    presentations=tk.Listbox(left,exportselection=False)
    presentations.pack(fill="both",expand=True)
    ttk.Label(right,text="Discovered sources").pack(anchor="w")
    entries=tk.Listbox(right,exportselection=False,height=10)
    entries.pack(fill="both",expand=True)
    detail=tk.Text(right,height=16,wrap="word")
    detail.pack(fill="both",expand=True,pady=6)
    rationale=ttk.Entry(right)
    rationale.pack(fill="x",pady=4)
    rationale.insert(0,"Reason for disposition")
    operator=ttk.Entry(right)
    operator.pack(fill="x")
    operator.insert(0,"Local Operator")

    def show_entry(_=None):
        doc=current["report"]
        selected=entries.curselection()
        if not doc or not selected:return
        hit=doc["sources"][selected[0]]
        detail.delete("1.0","end")
        detail.insert("end",json.dumps(hit,indent=2,ensure_ascii=False)
                      +"\n\nOriginal source can be opened using the browser after independent review.")
    entries.bind("<<ListboxSelect>>",show_entry)

    def show_presentation(_=None):
        selected=presentations.curselection()
        if not selected:return
        path=docs[selected[0]]
        doc=json.loads(path.read_text(encoding="utf-8-sig"))
        if doc.get("schema")!="surveyor.presentation.v0":return
        current.update(path=path,report=doc)
        entries.delete(0,"end")
        for hit in doc["sources"]:
            entries.insert("end",str(hit["index"])+": "+hit["title"])
        detail.delete("1.0","end")
        detail.insert("end","Choose a discovery item. Claims: "+str(len(doc.get("claims",[])))+
                      "\nResearch verification: "+doc.get("research_verification","unknown"))
    presentations.bind("<<ListboxSelect>>",show_presentation)

    def refresh():
        docs.clear()
        presentations.delete(0,"end")
        for path in sorted((archive/"presentations").glob("*.json")):
            try:
                doc=json.loads(path.read_text(encoding="utf-8-sig"))
                if doc.get("schema")!="surveyor.presentation.v0":continue
                docs.append(path)
                presentations.insert("end",doc.get("suite","?")+": "+doc.get("query","?")[:65])
            except (OSError,ValueError):
                continue

    def decide(action):
        doc=current["report"]
        selected=entries.curselection()
        if not doc or not selected:
            messagebox.showerror("Select a source","Choose a presentation and source.")
            return
        name=operator.get().strip()
        why=rationale.get().strip()
        if not name or not why or why=="Reason for disposition":
            messagebox.showerror("Required details","Enter operator and a substantive rationale.")
            return
        try:
            from .core import JobStore
            from .handoff import create_handoff
            answer=record_decision(current["path"],selected[0]+1,action,name,why,archive=archive)
            if action=="investigate_further":
                store=JobStore("surveyor.sqlite3")
                try:
                    handoff=create_handoff(store,current["path"],selected[0]+1,why,archive=archive)
                finally:
                    store.close()
                answer["queued_handoff_job"]=handoff["job_id"]
            if action=="approve":
                answer["catalogue"]=catalogue.add(current["path"],selected[0]+1,archive)["id"]
            messagebox.showinfo("Decision recorded",json.dumps(answer,indent=2))
        except Exception as exc:
            messagebox.showerror("Operation failed",str(exc))

    controls=ttk.Frame(right)
    controls.pack(fill="x",pady=5)
    for label,action in [("Approve candidate","approve"),("Investigate further","investigate_further"),
                         ("Flag / correct","flag_correct"),("Save for later","save_for_later")]:
        ttk.Button(controls,text=label,command=lambda a=action:decide(a)).pack(side="left",padx=3)
    ttk.Button(left,text="Refresh",command=refresh).pack(fill="x")

    def import_local_media():
        selected=filedialog.askopenfilename(title="Import authorised audio/video",
              filetypes=[("Audio/video","*.wav *.mp3 *.flac *.m4a *.aac *.ogg *.opus *.aif *.aiff *.mp4 *.mov *.mkv *.webm"),("All files","*.*")])
        if not selected:
            return
        name=operator.get().strip()
        permission=rationale.get().strip()
        if not name or not permission or permission=="Reason for disposition":
            messagebox.showerror("Permission required",
                "Enter your operator name and the media permission/licence basis in the rationale field.")
            return
        try:
            from .media import import_media
            event=import_media(selected, archive,operator=name,licence_basis=permission)
            messagebox.showinfo("Media archived","SHA-256: "+event["sha256_hex"]+
                                "\\nOriginal recording preserved; no evidence verified.")
        except Exception as exc:
            messagebox.showerror("Import failed",str(exc))
    ttk.Button(left,text="Import Media",command=import_local_media).pack(fill="x",pady=4)
    refresh()
    def close():
        catalogue.close()
        root.destroy()
    root.protocol("WM_DELETE_WINDOW",close)
    root.mainloop()
