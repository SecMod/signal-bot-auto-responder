from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import threading
import re

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
        self.link_process=None
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
        tk.Button(f,text="LOAD / REFRESH FROM SIGNAL",command=self.load_groups,bg=PANEL2,fg=WHITE).grid(row=0,column=3,padx=5)
        tk.Label(self.content,text="Select groups below. Use the buttons to enable/disable them, or double-click a row to toggle.",bg=BG,fg=MUTED).pack(anchor="w")
        self.gtree=ttk.Treeview(self.content,columns=("name","id","enabled"),show="headings",selectmode="extended")
        self.gtree.heading("name",text="GROUP NAME"); self.gtree.heading("id",text="GROUP ID"); self.gtree.heading("enabled",text="ENABLED")
        self.gtree.column("name",width=300); self.gtree.column("id",width=520); self.gtree.column("enabled",width=110,anchor="center")
        self.gtree.pack(fill="both",expand=True,pady=8)
        self.gtree.bind("<Double-1>",lambda e:self.toggle_group())
        self.refresh_groups()
        buttons=tk.Frame(self.content,bg=BG); buttons.pack(fill="x")
        tk.Button(buttons,text="ENABLE SELECTED",command=lambda:self.set_selected_groups(True),bg=GREEN,fg=BG).pack(side="left",padx=3)
        tk.Button(buttons,text="DISABLE SELECTED",command=lambda:self.set_selected_groups(False),bg="#d6a900",fg=BG).pack(side="left",padx=3)
        tk.Button(buttons,text="SELECT ALL",command=lambda:self.gtree.selection_set(self.gtree.get_children()),bg=PANEL2,fg=WHITE).pack(side="left",padx=3)
        tk.Button(buttons,text="CLEAR SELECTION",command=lambda:self.gtree.selection_remove(self.gtree.selection()),bg=PANEL2,fg=WHITE).pack(side="left",padx=3)
        tk.Button(buttons,text="REMOVE SELECTED",command=self.remove_group,bg=RED,fg=BG).pack(side="right")

    def refresh_groups(self):
        if not hasattr(self,"gtree"):return
        for i in self.gtree.get_children():self.gtree.delete(i)
        for g in self.storage.get_groups():self.gtree.insert("","end",iid=str(g["id"]),values=(g["name"],g["group_id"],"YES" if g["enabled"] else "NO"))

    def add_group(self):
        try:self.storage.add_group(self.gname.get(),self.gid.get());self.refresh_groups()
        except Exception as e:messagebox.showerror("Group",str(e))

    def set_selected_groups(self,enabled):
        selected=self.gtree.selection()
        if not selected:return messagebox.showwarning("Groups","Select at least one group.")
        for item in selected:
            self.storage.set_group_enabled(str(self.gtree.item(item)["values"][1]),enabled)
        self.refresh_groups()

    def toggle_group(self):
        selected=self.gtree.selection()
        if not selected:return
        item=selected[0]; values=self.gtree.item(item)["values"]
        self.storage.set_group_enabled(str(values[1]),str(values[2]).upper()!="YES")
        self.refresh_groups()
        if self.gtree.exists(item): self.gtree.selection_set(item)

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
        tk.Button(
            buttons,
            text="SEND IMAGE NOW",
            command=self.send_image_now,
            bg=PANEL2,
            fg=GREEN,
        ).pack(side="left",padx=4)

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

    def send_image_now(self):
        if not self.settings.signal_enabled:
            return messagebox.showwarning("Signal", "Enable Signal in Settings before sending.")
        if not self.settings.signal_account:
            return messagebox.showwarning("Signal", "Set or link the Signal account first.")
        groups = self.storage.get_groups(enabled_only=True)
        if not groups:
            return messagebox.showwarning("Signal", "Enable at least one authorized group first.")

        paths = filedialog.askopenfilenames(
            title="Select image(s) to send",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.webp *.bmp"),
                ("All files", "*.*"),
            ],
        )
        if not paths:
            return

        caption = simpledialog.askstring(
            "Image caption",
            "Optional caption (leave blank for no caption):",
            parent=self,
        )
        if caption is None:
            caption = ""

        try:
            from .signal_client import SignalClient
            client = SignalClient(
                self.settings.signal_account,
                self.settings.signal_cli_path or "signal-cli",
            )
            for group in groups:
                client.send_to_group(
                    group["group_id"],
                    caption,
                    attachments=list(paths),
                )
            self.storage.log(
                "INFO",
                f"REAL: sent {len(paths)} image(s) to {len(groups)} authorized group(s).",
            )
            messagebox.showinfo(
                "Signal",
                f"Sent {len(paths)} image(s) to {len(groups)} authorized group(s).",
            )
        except Exception as e:
            self.storage.log("ERROR", f"Image send failed: {e}")
            messagebox.showerror("Signal image send", str(e))

    def _view_settings(self):
        self._title("SETTINGS")
        f=tk.Frame(self.content,bg=BG);f.pack(anchor="w")
        self.svars={}
        vals=[("variation_count","Approved messages",self.settings.variation_count),("interval_minutes","Interval minutes",self.settings.interval_minutes),("cycle_hours","Cycle hours",self.settings.cycle_hours),("signal_account","Signal account",self.settings.signal_account),("signal_cli_path","signal-cli path",self.settings.signal_cli_path)]
        for r,(k,label,val) in enumerate(vals):
            tk.Label(f,text=label,bg=BG,fg=WHITE).grid(row=r,column=0,sticky="w",pady=5);e=tk.Entry(f,width=60);e.insert(0,str(val));e.grid(row=r,column=1,pady=5);self.svars[k]=e
        self.sig=tk.BooleanVar(value=self.settings.signal_enabled);tk.Checkbutton(f,text="Signal enabled",variable=self.sig,bg=BG,fg=WHITE,selectcolor=PANEL).grid(row=5,column=1,sticky="w")
        tk.Button(f,text="SAVE SETTINGS",command=self.save_settings,bg=GREEN,fg=BG).grid(row=6,column=1,sticky="w",pady=10)
        tk.Button(f,text="LINK SIGNAL ACCOUNT",command=self.link_signal_account,bg=PANEL2,fg=GREEN).grid(row=7,column=1,sticky="w",pady=(2,5))
        tk.Label(f,text="Links this app as a secondary Signal device. Scan the QR code with Signal → Settings → Linked Devices.",bg=BG,fg=MUTED,wraplength=700,justify="left").grid(row=8,column=1,sticky="w")

    def link_signal_account(self):
        if self.link_process and self.link_process.poll() is None:
            return messagebox.showwarning("Signal","A Signal linking session is already running.")
        cli=self.svars["signal_cli_path"].get().strip() or self.settings.signal_cli_path or "signal-cli"
        try:
            from .signal_client import SignalClient
            self.link_process=SignalClient("",cli).link("Signal Bot")
        except Exception as e:
            messagebox.showerror("Signal linking",str(e))
            return
        win=tk.Toplevel(self); win.title("Link Signal Account"); win.geometry("560x680"); win.configure(bg=BG)
        tk.Label(win,text="LINK SIGNAL ACCOUNT",bg=BG,fg=GREEN,font=("Segoe UI",18,"bold")).pack(pady=(15,5))
        tk.Label(win,text="Open Signal → Settings → Linked Devices → Link New Device, then scan this QR code.",bg=BG,fg=WHITE,wraplength=500,justify="center").pack(pady=5)
        qr_label=tk.Label(win,bg=BG); qr_label.pack(pady=10)
        status=tk.Label(win,text="Starting signal-cli…",bg=BG,fg=MUTED,wraplength=500,justify="center"); status.pack(pady=5)
        output=tk.Text(win,height=7,bg="#09100d",fg=MUTED,wrap="word"); output.pack(fill="both",expand=True,padx=15,pady=10)
        def append(text): output.insert("end",text); output.see("end")
        def show_qr(uri):
            try:
                import qrcode
                from PIL import ImageTk
                img=qrcode.make(uri).convert("RGB"); img.thumbnail((420,420))
                photo=ImageTk.PhotoImage(img); qr_label.configure(image=photo); qr_label.image=photo
                status.configure(text="QR code ready. Scan it from Signal → Settings → Linked Devices.")
            except Exception as e:
                status.configure(text=f"QR generation failed: {e}"); append(f"\nLink URI: {uri}\n")
        def reader():
            collected=""; uri=None
            try:
                for line in self.link_process.stdout:
                    collected += line; self.after(0,append,line)
                    if uri is None:
                        from .signal_client import SignalClient
                        uri=SignalClient.extract_link_uri(collected)
                        if uri: self.after(0,show_qr,uri)
                rc=self.link_process.wait()
                match=re.search(r"Associated with:\s*(\+\d+)",collected)
                account=match.group(1) if match else None
                def finished():
                    if rc==0 and account:
                        self.settings=Settings(self.settings.interval_minutes,self.settings.variation_count,self.settings.cycle_hours,account,True,cli)
                        self.storage.set_settings({"signal_account":account,"signal_enabled":True,"signal_cli_path":cli})
                        status.configure(text=f"Linked successfully as {account}.")
                        self.storage.log("INFO",f"Signal account linked: {account}")
                        self.svars["signal_account"].delete(0,"end"); self.svars["signal_account"].insert(0,account); self.sig.set(True)
                    elif rc==0: status.configure(text="Linking completed, but signal-cli did not report the account number.")
                    else: status.configure(text="Signal linking failed. See output below.")
                self.after(0,finished)
            except Exception as e:
                self.after(0,lambda:status.configure(text=f"Linking error: {e}"))
        threading.Thread(target=reader,daemon=True,name="signal-link").start()
        def close():
            if self.link_process and self.link_process.poll() is None: self.link_process.terminate()
            win.destroy()
        win.protocol("WM_DELETE_WINDOW",close)

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
