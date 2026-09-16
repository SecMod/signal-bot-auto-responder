from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
import threading

from .config import Settings
from .daily_content import generate_variations
from .storage import Storage


BG="#070a09"; PANEL="#101815"; PANEL2="#131d18"; GREEN="#39ff88"; WHITE="#f2fff8"; MUTED="#8da99b"; RED="#ff5c6c"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SIGNAL BOT — Control Panel")
        self.geometry("1250x820")
        self.minsize(1000,700)
        self.configure(bg=BG)
        self.storage=Storage()
        self.settings=self._load_settings()
        self.scheduler=None
        self.vars=[]
        self.content=tk.Frame(self,bg=BG)
        self._build_nav()
        self.content.pack(fill="both",expand=True,padx=15,pady=15)
        self.show("generator")

    def _load_settings(self):
        base=Settings.from_env()
        return Settings(
            int(self.storage.get_setting("interval_minutes",base.interval_minutes)),
            int(self.storage.get_setting("variation_count",base.variation_count)),
            int(self.storage.get_setting("cycle_hours",base.cycle_hours)),
            self.storage.get_setting("signal_account",base.signal_account),
            str(self.storage.get_setting("signal_enabled",str(base.signal_enabled))).lower()=="true",
            self.storage.get_setting("signal_cli_path",base.signal_cli_path),
        )

    def _build_nav(self):
        bar=tk.Frame(self,bg=PANEL); bar.pack(fill="x")
        for key,label in [("generator","Message Generator"),("packs","Saved Packs"),("groups","Authorized Groups"),("scheduler","Scheduler"),("settings","Settings"),("logs","Logs")]:
            tk.Button(bar,text=label,command=lambda k=key:self.show(k),bg=PANEL2,fg=WHITE,relief="flat",padx=14,pady=10).pack(side="left",padx=2,pady=2)

    def clear(self):
        for w in self.content.winfo_children(): w.destroy()

    def show(self,key):
        self.clear()
        getattr(self,"_view_"+key)()

    def _title(self,text):
        tk.Label(self.content,text=text,bg=BG,fg=GREEN,font=("Segoe UI",20,"bold")).pack(anchor="w",pady=(0,10))

    def _view_generator(self):
        self._title("MESSAGE GENERATOR")
        self.source=tk.Text(self.content,height=7,bg="#09100d",fg=WHITE,insertbackground=GREEN,wrap="word")
        self.source.pack(fill="x",pady=8)
        tk.Button(self.content,text="GENERATE 24 VARIATIONS",command=self.generate,bg=GREEN,fg=BG).pack(anchor="w")

        # Scrollable review area. The save button stays outside the scrolling
        # canvas so it is always visible even when all 24 variations are shown.
        review_shell=tk.Frame(self.content,bg=BG)
        review_shell.pack(fill="both",expand=True,pady=(10,4))

        self.review_canvas=tk.Canvas(review_shell,bg=BG,highlightthickness=0)
        self.review_scrollbar=ttk.Scrollbar(review_shell,orient="vertical",command=self.review_canvas.yview)
        self.review_canvas.configure(yscrollcommand=self.review_scrollbar.set)

        self.review_scrollbar.pack(side="right",fill="y")
        self.review_canvas.pack(side="left",fill="both",expand=True)

        self.review=tk.Frame(self.review_canvas,bg=BG)
        self.review_window=self.review_canvas.create_window((0,0),window=self.review,anchor="nw")

        self.review.bind(
            "<Configure>",
            lambda e:self.review_canvas.configure(scrollregion=self.review_canvas.bbox("all"))
        )
        self.review_canvas.bind(
            "<Configure>",
            lambda e:self.review_canvas.itemconfigure(self.review_window,width=e.width)
        )
        self.review_canvas.bind("<MouseWheel>",self._review_mousewheel)
        self.review.bind("<MouseWheel>",self._review_mousewheel)

        self.save_button=tk.Button(
            self.content,
            text="SAVE APPROVED PACK",
            command=self.save_pack,
            bg=GREEN,
            fg=BG,
            font=("Segoe UI",10,"bold"),
            padx=16,
            pady=8,
        )
        self.save_button.pack(anchor="e",pady=(4,0))

    def _review_mousewheel(self,event):
        self.review_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        return "break"

    def generate(self):
        src=self.source.get("1.0","end").strip()
        if not src:return messagebox.showwarning("Message","Enter a message first.")
        for w in self.review.winfo_children():w.destroy()
        self.vars=[]
        for i,m in enumerate(generate_variations(src,24),1):
            row=tk.Frame(self.review,bg=PANEL); row.pack(fill="x",pady=2)
            v=tk.BooleanVar(value=True)
            tk.Checkbutton(row,text=f"{i:02d}",variable=v,bg=PANEL,fg=GREEN,selectcolor=BG).pack(side="left")
            box=tk.Text(row,height=2,bg="#09100d",fg=WHITE,insertbackground=GREEN,wrap="word")
            box.insert("1.0",m)
            box.pack(side="left",fill="x",expand=True)
            self.vars.append((v,box))
        self.review.update_idletasks()
        self.review_canvas.configure(scrollregion=self.review_canvas.bbox("all"))
        self.review_canvas.yview_moveto(0)

    def save_pack(self):
        try:
            src=self.source.get("1.0","end").strip()
            vals=[b.get("1.0","end").strip() for v,b in self.vars if v.get() and b.get("1.0","end").strip()]
            if len(vals)!=24:return messagebox.showwarning("Approval","All 24 variations must be approved before saving.")
            pid=self.storage.save_pack(src,vals)
            self.storage.log("INFO",f"Saved pack #{pid}")
            messagebox.showinfo("Saved",f"Pack #{pid} saved.")
        except Exception as e:
            self.storage.log("ERROR",f"Pack save failed: {e}")
            messagebox.showerror("Saved Pack",str(e))

    def _view_packs(self):
        self._title("SAVED PACKS")
        tree=ttk.Treeview(self.content,columns=("id","date","source","count","approved"),show="headings")
        for c in tree["columns"]:tree.heading(c,text=c.upper())
        tree.pack(fill="both",expand=True)
        for p in self.storage.list_packs():tree.insert("","end",iid=str(p["id"]),values=(p["id"],p["created_at"],p["source"][:100],p["variation_count"],p["approved_count"]))
        buttons=tk.Frame(self.content,bg=BG);buttons.pack(fill="x",pady=8)
        tk.Button(buttons,text="OPEN SELECTED",command=lambda:self.open_pack(tree),bg=PANEL2,fg=WHITE).pack(side="left")
        tk.Button(buttons,text="DELETE SELECTED",command=lambda:self.delete_pack(tree),bg=RED,fg=BG).pack(side="right")

    def open_pack(self,tree):
        s=tree.selection()
        if not s:return
        p=self.storage.get_pack(int(s[0])); self._edit_pack(p)

    def _edit_pack(self,p):
        self.clear(); self._title(f"PACK #{p['id']} — EDIT")
        tk.Label(self.content,text=p["source"],bg=BG,fg=MUTED,wraplength=1000).pack(anchor="w")
        rows=tk.Frame(self.content,bg=BG);rows.pack(fill="both",expand=True,pady=10)
        edits=[]
        for v in p["variations"]:
            row=tk.Frame(rows,bg=PANEL);row.pack(fill="x",pady=2)
            a=tk.BooleanVar(value=bool(v["approved"]));tk.Checkbutton(row,variable=a,bg=PANEL,selectcolor=BG).pack(side="left")
            e=tk.Entry(row,bg="#09100d",fg=WHITE,insertbackground=GREEN);e.insert(0,v["text"]);e.pack(side="left",fill="x",expand=True,padx=5)
            edits.append((v["id"],a,e))
        def save():
            try:
                for vid,a,e in edits:self.storage.set_variation(vid,e.get(),a.get())
                self.storage.log("INFO",f"Updated pack #{p['id']}");self.show("packs")
            except Exception as e:messagebox.showerror("Pack",str(e))
        tk.Button(self.content,text="SAVE CHANGES",command=save,bg=GREEN,fg=BG).pack(anchor="e")

    def delete_pack(self,tree):
        s=tree.selection()
        if not s:return
        if not messagebox.askyesno("Delete","Delete selected pack?"):return
        try:
            self.storage.delete_pack(int(s[0]))
            self.storage.log("INFO",f"Deleted pack #{s[0]}")
            self.show("packs")
        except Exception as e:
            self.storage.log("ERROR",f"Pack delete failed: {e}")
            messagebox.showerror("Delete Pack",str(e))

    def _view_groups(self):
        self._title("AUTHORIZED SIGNAL GROUPS")
        f=tk.Frame(self.content,bg=BG);f.pack(fill="x",pady=8)
        self.gname=tk.Entry(f,width=25);self.gid=tk.Entry(f,width=45)
        self.gname.grid(row=0,column=0);self.gid.grid(row=0,column=1,padx=5)
        tk.Button(f,text="ADD GROUP",command=self.add_group,bg=GREEN,fg=BG).grid(row=0,column=2)
        tk.Button(f,text="LOAD FROM SIGNAL ACCOUNT",command=self.load_groups,bg=PANEL2,fg=WHITE).grid(row=0,column=3,padx=5)
        self.gtree=ttk.Treeview(self.content,columns=("name","id","enabled"),show="headings",selectmode="extended")
        for c in self.gtree["columns"]:self.gtree.heading(c,text=c.upper())
        self.gtree.pack(fill="both",expand=True,pady=8);self.refresh_groups()
        tk.Button(self.content,text="ENABLE SELECTED",command=lambda:self.set_selected_groups(True),bg=GREEN,fg=BG).pack(side="left",padx=3)
        tk.Button(self.content,text="DISABLE SELECTED",command=lambda:self.set_selected_groups(False),bg="#d6a900",fg=BG).pack(side="left",padx=3)
        tk.Button(self.content,text="REMOVE SELECTED",command=self.remove_group,bg=RED,fg=BG).pack(side="right")

    def refresh_groups(self):
        if not hasattr(self,"gtree"):return
        for i in self.gtree.get_children():self.gtree.delete(i)
        for g in self.storage.get_groups():self.gtree.insert("","end",iid=str(g["id"]),values=(g["name"],g["group_id"],"YES" if g["enabled"] else "NO"))

    def add_group(self):
        try:self.storage.add_group(self.gname.get(),self.gid.get());self.refresh_groups()
        except Exception as e:messagebox.showerror("Group",str(e))

    def set_selected_groups(self,enabled):
        for item in self.gtree.selection():
            self.storage.set_group_enabled(self.gtree.item(item)["values"][1],enabled)
        self.refresh_groups()

    def remove_group(self):
        for item in self.gtree.selection():
            self.storage.remove_group(self.gtree.item(item)["values"][1])
        self.refresh_groups()

    def load_groups(self):
        if not self.settings.signal_account:return messagebox.showwarning("Signal","Configure a Signal account first.")
        from .signal_client import SignalClient
        try:
            groups=SignalClient(self.settings.signal_account,self.settings.signal_cli_path or "signal-cli").list_groups()
            existing={g["group_id"] for g in self.storage.get_groups()}
            added=0
            for g in groups:
                if g["group_id"] in existing:continue
                try:
                    self.storage.add_group(g["name"],g["group_id"],enabled=False)
                    added += 1
                    existing.add(g["group_id"])
                except Exception:
                    continue
            self.storage.log("INFO",f"Loaded {len(groups)} Signal groups; added {added} new groups as disabled.")
            self.refresh_groups()
            messagebox.showinfo("Signal groups",f"Loaded {len(groups)} groups. {added} new groups were added as DISABLED. Enable only authorized groups.")
        except Exception as e:
            self.storage.log("ERROR",f"Signal group load failed: {e}")
            messagebox.showerror("Signal",str(e))

    def _view_scheduler(self):
        self._title("SCHEDULER")
        state="RUNNING" if self.scheduler and self.scheduler.running else "STOPPED"
        tk.Label(self.content,text=f"Status: {state}\nApproved messages: {self.settings.variation_count}\nInterval: {self.settings.interval_minutes} minutes\nCycle: {self.settings.cycle_hours} hours\nSignal enabled: {'YES' if self.settings.signal_enabled else 'NO'}",bg=BG,fg=WHITE,justify="left").pack(anchor="w",pady=10)
        tk.Label(self.content,text="Pack to use:",bg=BG,fg=WHITE).pack(anchor="w")
        self.pack_choice=tk.StringVar()
        self.pack_combo=ttk.Combobox(self.content,textvariable=self.pack_choice,state="readonly",width=80)
        pack_rows=self.storage.list_packs()
        self.pack_map={f'#{p["id"]} | {p["source"][:70]}':p["id"] for p in pack_rows}
        self.pack_combo["values"]=list(self.pack_map)
        if self.pack_combo["values"]: self.pack_combo.current(0)
        self.pack_combo.pack(anchor="w",pady=(2,10))
        buttons=tk.Frame(self.content,bg=BG);buttons.pack(anchor="w")
        tk.Button(buttons,text="START PREVIEW / DRY RUN",command=lambda:self.start_scheduler(False),bg=GREEN,fg=BG).pack(side="left",padx=4)
        tk.Button(buttons,text="START REAL (AUTHORIZED)",command=lambda:self.start_scheduler(True),bg="#d6a900",fg=BG).pack(side="left",padx=4)
        tk.Button(buttons,text="STOP",command=self.stop_scheduler,bg=RED,fg=BG).pack(side="left",padx=4)

    def _reload_scheduler_view(self):
        if not self.winfo_exists():return
        self.after(0, lambda:self.show("scheduler") if self.winfo_exists() else None)

    def start_scheduler(self, real=False):
        if self.scheduler and self.scheduler.running:return
        if not getattr(self,"pack_map",{}):return messagebox.showwarning("Scheduler","Save a pack first.")
        pid=self.pack_map.get(self.pack_choice.get())
        if not pid:return messagebox.showwarning("Scheduler","Select a saved pack first.")
        p=self.storage.get_pack(pid)
        if not p:return messagebox.showwarning("Scheduler","Selected pack no longer exists.")
        msgs=[v["text"] for v in p["variations"] if v["approved"]][:self.settings.variation_count]
        if len(msgs)!=self.settings.variation_count:return messagebox.showwarning("Scheduler",f"Need {self.settings.variation_count} approved variations; pack has {len(msgs)}.")
        if real:
            if not self.settings.signal_enabled:return messagebox.showwarning("Signal","Enable Signal in Settings before starting real mode.")
            if not self.settings.signal_account:return messagebox.showwarning("Signal","Set the Signal account before starting real mode.")
            if not self.storage.get_groups(enabled_only=True):return messagebox.showwarning("Signal","Enable at least one authorized group before starting real mode.")
            from .main import build_sender
            process=build_sender(self.settings,self.storage); mode="real"
        else:
            process=lambda m:self.storage.log("INFO",f"PREVIEW: {m[:160]}"); mode="preview"
        from .scheduler import Scheduler
        self.scheduler=Scheduler(msgs,self.settings.interval_minutes,self.settings.cycle_hours)
        try:
            self.scheduler.start(process)
            self.storage.log("INFO",f"Scheduler started ({mode}) using pack #{pid}")
            self.show("scheduler")
        except Exception as e:
            self.storage.log("ERROR",f"Scheduler start failed: {e}")
            self.scheduler=None
            messagebox.showerror("Scheduler",str(e))

    def stop_scheduler(self):
        if self.scheduler:self.scheduler.stop();self.storage.log("INFO","Scheduler stopped")
        self.show("scheduler")

    def _view_settings(self):
        self._title("SETTINGS")
        f=tk.Frame(self.content,bg=BG);f.pack(anchor="w")
        self.svars={}
        vals=[("variation_count","Approved messages",self.settings.variation_count),("interval_minutes","Interval minutes",self.settings.interval_minutes),("cycle_hours","Cycle hours",self.settings.cycle_hours),("signal_account","Signal account",self.settings.signal_account),("signal_cli_path","signal-cli path",self.settings.signal_cli_path)]
        for r,(k,label,val) in enumerate(vals):
            tk.Label(f,text=label,bg=BG,fg=WHITE).grid(row=r,column=0,sticky="w",pady=5);e=tk.Entry(f,width=60);e.insert(0,str(val));e.grid(row=r,column=1,pady=5);self.svars[k]=e
        self.sig=tk.BooleanVar(value=self.settings.signal_enabled);tk.Checkbutton(f,text="Signal enabled",variable=self.sig,bg=BG,fg=WHITE,selectcolor=PANEL).grid(row=5,column=1,sticky="w")
        tk.Button(f,text="SAVE SETTINGS",command=self.save_settings,bg=GREEN,fg=BG).grid(row=6,column=1,sticky="w",pady=10)

    def save_settings(self):
        try:
            values={"variation_count":int(self.svars["variation_count"].get()),"interval_minutes":int(self.svars["interval_minutes"].get()),"cycle_hours":int(self.svars["cycle_hours"].get()),"signal_account":self.svars["signal_account"].get().strip(),"signal_cli_path":self.svars["signal_cli_path"].get().strip(),"signal_enabled":self.sig.get()}
            if any(values[k]<=0 for k in ("variation_count","interval_minutes","cycle_hours")):raise ValueError("Numeric settings must be greater than zero.")
            if self.scheduler and self.scheduler.running:raise ValueError("Stop the scheduler before changing scheduler settings.")
            self.settings=Settings(**values);self.storage.set_settings(values);self.storage.log("INFO","Settings saved");messagebox.showinfo("Settings","Settings saved and will be used by the next scheduler start.")
        except Exception as e:messagebox.showerror("Settings",str(e))

    def _view_logs(self):
        self._title("LOGS")
        box=tk.Text(self.content,bg="#09100d",fg=WHITE);box.pack(fill="both",expand=True)
        for r in reversed(self.storage.get_logs(500)):box.insert("end",f"{r['created_at']} | {r['level']} | {r['message']}\n")

def main():App().mainloop()

if __name__=="__main__":main()
