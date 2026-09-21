from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import threading
import re
import os
from datetime import datetime

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
        self.scheduler_media_paths=[]
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
        self.load_groups_button=tk.Button(
            f,text="LOAD / REFRESH FROM SIGNAL",command=self.load_groups,
            bg=PANEL2,fg=WHITE,
        )
        self.load_groups_button.grid(row=0,column=3,padx=5)
        self.groups_status=tk.Label(
            self.content,text="Ready",bg=BG,fg=MUTED
        )
        self.groups_status.pack(anchor="w",pady=(0,3))
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
        if not self.settings.signal_account:
            return messagebox.showwarning("Signal","Configure a Signal account first.")

        # Never run signal-cli synchronously on Tkinter's main thread.
        # receive/listGroups can block when signal-cli is busy or its local
        # config is locked; doing that here makes the entire GUI appear hung.
        button = getattr(self, "load_groups_button", None)
        if button is not None:
            button.configure(state="disabled")
        status = getattr(self, "groups_status", None)
        if status is not None:
            status.configure(text="Loading groups from Signal…")

        from .signal_client import SignalClient

        def worker():
            try:
                client=SignalClient(
                    self.settings.signal_account,
                    self.settings.signal_cli_path or "signal-cli",
                )
                groups=client.list_groups()
                existing={g["group_id"] for g in self.storage.get_groups()}
                added=0
                for g in groups:
                    if g["group_id"] in existing:
                        continue
                    try:
                        self.storage.add_group(g["name"],g["group_id"],enabled=False)
                        added += 1
                        existing.add(g["group_id"])
                    except Exception:
                        continue
                self.storage.log(
                    "INFO",
                    f"Signal group refresh completed: {len(groups)} groups found; {added} new groups added as disabled.",
                )
                self.after(0,lambda:self._groups_load_finished(len(groups),added,None))
            except Exception as e:
                self.storage.log("ERROR",f"Signal group load failed: {e}")
                self.after(0,lambda err=str(e):self._groups_load_finished(0,0,err))

        threading.Thread(target=worker,daemon=True,name="signal-groups-loader").start()

    def _groups_load_finished(self,count,added,error):
        button = getattr(self, "load_groups_button", None)
        if button is not None:
            button.configure(state="normal")
        status = getattr(self, "groups_status", None)
        if status is not None:
            status.configure(
                text=(
                    f"Signal group list updated • {count} groups found • {added} new groups added as DISABLED."
                    if error is None
                    else f"Signal group update failed: {error}"
                )
            )
        self.refresh_groups()
        if error is None:
            messagebox.showinfo(
                "Signal groups updated",
                f"Signal group list updated successfully.\n\n"
                f"Groups found: {count}\n"
                f"New groups added: {added}\n"
                "New groups were added as DISABLED. Enable only authorized groups.",
            )
        else:
            messagebox.showerror("Signal",error)

    def _view_scheduler(self):
        self._title("SCHEDULER — 24/7 CONTROL")
        state="ONLINE" if self.scheduler and self.scheduler.running else "OFFLINE"
        state_fg=GREEN if state=="ONLINE" else RED

        # Status header
        status=tk.Frame(self.content,bg=PANEL,padx=16,pady=12)
        status.pack(fill="x",pady=(0,10))
        left=tk.Frame(status,bg=PANEL); left.pack(side="left",fill="x",expand=True)
        tk.Label(
            left,text=f"● BOT {state}",bg=PANEL,fg=state_fg,
            font=("Segoe UI",14,"bold"),
        ).pack(anchor="w")
        tk.Label(
            left,
            text="24/7 scheduler service • GUI is the control panel",
            bg=PANEL,fg=MUTED,
        ).pack(anchor="w",pady=(3,0))

        self.scheduler_status_label=tk.Label(
            left,
            text=f"● BOT {state}",
            bg=PANEL,
            fg=state_fg,
            font=("Segoe UI",14,"bold"),
        )
        self.scheduler_status_label.pack(anchor="w")
        self.scheduler_uptime_label=tk.Label(
            left,
            text="UPTIME 00:00:00" if state=="ONLINE" else "UPTIME —",
            bg=PANEL,
            fg=MUTED,
        )
        self.scheduler_uptime_label.pack(anchor="w",pady=(3,0))

        stats=tk.Frame(status,bg=PANEL); stats.pack(side="right")
        for col,title in enumerate(("NEXT POST","LAST POST","POSTS TODAY","SKIPPED")):
            tk.Label(stats,text=title,bg=PANEL,fg=MUTED).grid(row=0,column=col,padx=18)
        self.scheduler_next_label=tk.Label(stats,text="—",bg=PANEL,fg=WHITE,font=("Segoe UI",11,"bold"))
        self.scheduler_last_label=tk.Label(stats,text="—",bg=PANEL,fg=WHITE,font=("Segoe UI",11,"bold"))
        self.scheduler_posts_label=tk.Label(stats,text="0",bg=PANEL,fg=WHITE,font=("Segoe UI",11,"bold"))
        self.scheduler_skipped_label=tk.Label(stats,text="0",bg=PANEL,fg=WHITE,font=("Segoe UI",11,"bold"))
        for col,label in enumerate((self.scheduler_next_label,self.scheduler_last_label,self.scheduler_posts_label,self.scheduler_skipped_label)):
            label.grid(row=1,column=col)

        # Mode selector
        mode_box=tk.Frame(self.content,bg=BG)
        mode_box.pack(fill="x",pady=4)
        tk.Label(mode_box,text="MODE",bg=BG,fg=WHITE,font=("Segoe UI",11,"bold")).pack(anchor="w")
        mode_row=tk.Frame(mode_box,bg=BG); mode_row.pack(anchor="w",pady=5)
        self.scheduler_mode=tk.StringVar(
            value=self.storage.get_setting("scheduler_mode","normal")
        )
        for value,label in (("normal","NORMAL MODE"),("safe","SAFE MODE")):
            tk.Radiobutton(
                mode_row,text=label,variable=self.scheduler_mode,value=value,
                bg=PANEL2,fg=WHITE,selectcolor=BG,
                activebackground=PANEL2,activeforeground=GREEN,
                padx=18,pady=8,
            ).pack(side="left",padx=(0,8))
        self.scheduler_mode.trace_add("write",lambda *_: self._scheduler_mode_changed())

        # Pack
        pack_box=tk.Frame(self.content,bg=PANEL,padx=14,pady=12)
        pack_box.pack(fill="x",pady=8)
        tk.Label(pack_box,text="PACK",bg=PANEL,fg=MUTED,font=("Segoe UI",9,"bold")).pack(anchor="w")
        self.pack_choice=tk.StringVar()
        self.pack_combo=ttk.Combobox(
            pack_box,textvariable=self.pack_choice,state="readonly",width=90
        )
        pack_rows=self.storage.list_packs()
        self.pack_map={f'#{p["id"]} | {p["source"][:80]}':p["id"] for p in pack_rows}
        self.pack_combo["values"]=list(self.pack_map)
        if self.pack_combo["values"]: self.pack_combo.current(0)
        self.pack_combo.pack(fill="x",pady=(5,0))

        # Media
        media_box=tk.Frame(self.content,bg=PANEL,padx=14,pady=12)
        media_box.pack(fill="x",pady=8)
        tk.Label(media_box,text="MEDIA",bg=PANEL,fg=MUTED,font=("Segoe UI",9,"bold")).pack(anchor="w")
        media_row=tk.Frame(media_box,bg=PANEL); media_row.pack(fill="x",pady=(5,0))
        self.scheduler_media_label=tk.Label(
            media_row,text=self._scheduler_media_text(),bg=PANEL,fg=WHITE,
            justify="left",anchor="w",wraplength=780,
        )
        self.scheduler_media_label.pack(side="left",fill="x",expand=True)
        tk.Button(
            media_row,text="ADD MEDIA",command=self.select_scheduler_media,
            bg=PANEL2,fg=GREEN,padx=12,
        ).pack(side="right",padx=3)
        tk.Button(
            media_row,text="CLEAR",command=self.clear_scheduler_media,
            bg=PANEL2,fg=WHITE,padx=12,
        ).pack(side="right",padx=3)

        # Mode-specific configuration
        config_box=tk.Frame(self.content,bg=PANEL,padx=14,pady=12)
        config_box.pack(fill="x",pady=8)

        selected_mode=self.scheduler_mode.get()
        if selected_mode=="safe":
            config_title="SAFE MODE CONFIGURATION"
            config_values=(
                ("Minimum interval","60 min"),
                ("Daily limit","8 / group / 24h"),
                ("Duplicate cooldown","24 hours"),
                ("Quiet hours","23:00 → 08:00"),
                ("Uncertain actions","SKIP"),
                ("Logging","ON"),
            )
            config_note="Conservative posting limits. Safe Mode enforcement is not yet active in the delivery layer."
        else:
            config_title="NORMAL MODE CONFIGURATION"
            config_values=(
                ("Interval",f"{self.settings.interval_minutes} min"),
                ("Cycle setting",f"{self.settings.cycle_hours} hours"),
                ("Approved messages",str(self.settings.variation_count)),
                ("Authorized groups",str(len(self.storage.get_groups(enabled_only=True)))),
                ("Selected media",f"{len(self.scheduler_media_paths)} / 3"),
                ("Duplicate protection","OFF"),
            )
            config_note="Uses the scheduler settings saved in Settings without the Safe Mode limits."

        tk.Label(
            config_box,text=config_title,bg=PANEL,fg=MUTED,
            font=("Segoe UI",9,"bold"),
        ).pack(anchor="w")

        config_grid=tk.Frame(config_box,bg=PANEL)
        config_grid.pack(fill="x",pady=(7,0))
        for i,(label,value) in enumerate(config_values):
            col=tk.Frame(config_grid,bg=PANEL)
            col.grid(row=0,column=i,sticky="w",padx=(0,28))
            tk.Label(col,text=label,bg=PANEL,fg=MUTED).pack(anchor="w")
            value_label=tk.Label(
                col,text=value,bg=PANEL,fg=WHITE,
                font=("Segoe UI",10,"bold"),
            )
            value_label.pack(anchor="w",pady=(2,0))
            if label=="Selected media":
                self.config_media_value=value_label

        tk.Label(
            config_box,text=config_note,bg=PANEL,fg=MUTED,
            wraplength=1050,justify="left",
        ).pack(anchor="w",pady=(8,0))

        # Authorized groups
        groups=self.storage.get_groups(enabled_only=True)
        group_box=tk.Frame(self.content,bg=PANEL,padx=14,pady=10)
        group_box.pack(fill="x",pady=8)
        tk.Label(
            group_box,
            text=f"AUTHORIZED GROUPS   {len(groups)} ENABLED",
            bg=PANEL,fg=GREEN if groups else RED,
            font=("Segoe UI",9,"bold"),
        ).pack(anchor="w")

        controls=tk.Frame(self.content,bg=BG); controls.pack(fill="x",pady=(10,0))
        tk.Button(
            controls,text="START 24/7 BOT",
            command=lambda:self.start_scheduler(True),
            bg=GREEN,fg=BG,font=("Segoe UI",10,"bold"),padx=18,pady=9,
        ).pack(side="left",padx=4)
        tk.Button(
            controls,text="START PREVIEW",
            command=lambda:self.start_scheduler(False),
            bg=PANEL2,fg=WHITE,padx=18,pady=9,
        ).pack(side="left",padx=4)
        tk.Button(
            controls,text="STOP",
            command=self.stop_scheduler,
            bg=RED,fg=BG,font=("Segoe UI",10,"bold"),padx=18,pady=9,
        ).pack(side="left",padx=4)
        tk.Button(
            controls,text="SEND MEDIA NOW",
            command=self.send_media_now,
            bg=PANEL2,fg=GREEN,padx=18,pady=9,
        ).pack(side="right",padx=4)

    def _scheduler_runtime_state(self, state):
        self.after(0, self._update_scheduler_dashboard)

    def _scheduler_post_event(self, success, error):
        if success:
            self.storage.log("INFO", "Scheduler post completed.")
        self.after(0, self._update_scheduler_dashboard)

    def _scheduler_error_event(self, error):
        self.storage.log("ERROR", f"Scheduler delivery error: {error}")
        self.after(0, self._update_scheduler_dashboard)

    def _format_runtime_time(self, value):
        return value.strftime("%H:%M:%S") if value else "—"

    def _update_scheduler_dashboard(self):
        scheduler=self.scheduler
        if not hasattr(self,"scheduler_status_label"):
            return
        try:
            if not self.scheduler_status_label.winfo_exists():
                return
        except Exception:
            return

        running=bool(scheduler and scheduler.running)
        if running:
            fg=GREEN
            text="● BOT ONLINE"
        elif scheduler and scheduler.last_error:
            fg="#ffb000"
            text="● BOT ERROR"
        else:
            fg=RED
            text="● BOT OFFLINE"

        self.scheduler_status_label.configure(text=text,fg=fg)

        if running and scheduler and scheduler.started_at:
            elapsed=max(0,int((datetime.now()-scheduler.started_at).total_seconds()))
            h,rem=divmod(elapsed,3600)
            m,s=divmod(rem,60)
            self.scheduler_uptime_label.configure(text=f"UPTIME {h:02d}:{m:02d}:{s:02d}")
        else:
            self.scheduler_uptime_label.configure(text="UPTIME —")

        self.scheduler_next_label.configure(
            text=self._format_runtime_time(scheduler.next_post_at if scheduler else None)
        )
        self.scheduler_last_label.configure(
            text=self._format_runtime_time(scheduler.last_post_at if scheduler else None)
        )
        self.scheduler_posts_label.configure(
            text=str(scheduler.posts_today if scheduler else 0)
        )
        self.scheduler_skipped_label.configure(
            text=str(scheduler.skipped if scheduler else 0)
        )

        self.after(1000,self._update_scheduler_dashboard)

    def _scheduler_mode_changed(self):
        mode=self.scheduler_mode.get()
        self.storage.set_settings({"scheduler_mode":mode})
        # Refresh the dashboard so the selected mode is immediately visible.
        # Do not restart a running scheduler automatically.
        if hasattr(self,"_scheduler_mode_refresh_pending") and self._scheduler_mode_refresh_pending:
            return
        self._scheduler_mode_refresh_pending=True
        self.after(100,self._finish_scheduler_mode_refresh)

    def _finish_scheduler_mode_refresh(self):
        self._scheduler_mode_refresh_pending=False
        if self.winfo_exists():
            self.show("scheduler")

    def _reload_scheduler_view(self):
        if not self.winfo_exists():return
        self.after(0, lambda:self.show("scheduler") if self.winfo_exists() else None)

    def _scheduler_media_text(self):
        if not self.scheduler_media_paths:
            return "Scheduled media: NONE — messages will be sent as text only."
        names = "\n".join(
            f"  {i}. {os.path.basename(path)}"
            for i, path in enumerate(self.scheduler_media_paths, 1)
        )
        return (
            "Scheduled media (attached to every pack message):\n"
            + names
        )

    def select_scheduler_media(self):
        # Use a dedicated 3-slot picker instead of relying on the native
        # multi-select file dialog, which can behave differently across
        # Linux/Tk desktop environments.
        win=tk.Toplevel(self)
        win.title("Select Scheduled Media (1–3)")
        win.geometry("760x300")
        win.configure(bg=BG)
        win.transient(self)
        win.grab_set()

        tk.Label(
            win,
            text="SELECT SCHEDULED MEDIA (1–3)",
            bg=BG,
            fg=GREEN,
            font=("Segoe UI",16,"bold"),
        ).pack(pady=(15,5))
        tk.Label(
            win,
            text="Choose up to 3 images/videos. Each slot can be selected separately.",
            bg=BG,
            fg=MUTED,
        ).pack(pady=(0,10))

        allowed_extensions = {
            ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp",
            ".mp4", ".mov", ".webm", ".avi", ".mkv",
        }
        selected=list(self.scheduler_media_paths)
        rows=tk.Frame(win,bg=BG)
        rows.pack(fill="x",padx=20)

        row_labels=[]
        def refresh_rows():
            for i,label in enumerate(row_labels):
                path=selected[i] if i < len(selected) else ""
                label.configure(text=os.path.basename(path) if path else "— no media selected —")

        def browse_slot(index):
            path=filedialog.askopenfilename(
                parent=win,
                title=f"Select media {index+1} of 3",
                filetypes=[
                    ("Images and videos","*.png *.jpg *.jpeg *.gif *.webp *.bmp *.mp4 *.mov *.webm *.avi *.mkv"),
                    ("Image files","*.png *.jpg *.jpeg *.gif *.webp *.bmp"),
                    ("Video files","*.mp4 *.mov *.webm *.avi *.mkv"),
                    ("All files","*.*"),
                ],
            )
            if not path:
                return
            if os.path.splitext(path)[1].lower() not in allowed_extensions:
                return messagebox.showwarning(
                    "Scheduled media",
                    "Unsupported media type selected.",
                    parent=win,
                )
            while len(selected) <= index:
                selected.append("")
            selected[index]=path
            while selected and not selected[-1]:
                selected.pop()
            refresh_rows()

        def remove_slot(index):
            if index < len(selected):
                selected.pop(index)
            refresh_rows()

        for i in range(3):
            row=tk.Frame(rows,bg=BG)
            row.pack(fill="x",pady=4)
            tk.Label(row,text=f"{i+1}.",width=3,bg=BG,fg=GREEN).pack(side="left")
            label=tk.Label(
                row,
                text="— no media selected —",
                bg="#09100d",
                fg=WHITE,
                anchor="w",
                padx=8,
            )
            label.pack(side="left",fill="x",expand=True,padx=5)
            row_labels.append(label)
            tk.Button(
                row,
                text="BROWSE",
                command=lambda i=i:browse_slot(i),
                bg=PANEL2,
                fg=GREEN,
            ).pack(side="left",padx=3)
            tk.Button(
                row,
                text="REMOVE",
                command=lambda i=i:remove_slot(i),
                bg=PANEL2,
                fg=WHITE,
            ).pack(side="left",padx=3)

        refresh_rows()

        actions=tk.Frame(win,bg=BG)
        actions.pack(fill="x",padx=20,pady=15)

        def apply_selection():
            cleaned=[p for p in selected if p]
            if not cleaned:
                self.scheduler_media_paths=[]
            elif len(cleaned)<=3:
                self.scheduler_media_paths=list(cleaned)
            if hasattr(self,"scheduler_media_label"):
                self.scheduler_media_label.configure(text=self._scheduler_media_text())
            # Refresh the dashboard configuration so the selected count is
            # immediately reflected as 1/3, 2/3, or 3/3.
            if hasattr(self,"config_media_value") and self.config_media_value.winfo_exists():
                self.config_media_value.configure(
                    text=f"{len(self.scheduler_media_paths)} / 3"
                )
            self.storage.log(
                "INFO",
                f"Scheduled media selected: {len(self.scheduler_media_paths)} file(s).",
            )
            win.destroy()

        tk.Button(
            actions,
            text="CANCEL",
            command=win.destroy,
            bg=PANEL2,
            fg=WHITE,
            padx=12,
        ).pack(side="right",padx=4)
        tk.Button(
            actions,
            text="USE SELECTED MEDIA",
            command=apply_selection,
            bg=GREEN,
            fg=BG,
            padx=12,
        ).pack(side="right",padx=4)

    def clear_scheduler_media(self):
        self.scheduler_media_paths = []
        if hasattr(self, "scheduler_media_label"):
            self.scheduler_media_label.configure(text=self._scheduler_media_text())

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
            process=build_sender(
                self.settings,
                self.storage,
                attachments=list(self.scheduler_media_paths),
            )
            mode="real"
        else:
            process=lambda m:self.storage.log("INFO",f"PREVIEW: {m[:160]}"); mode="preview"
        from .scheduler import Scheduler
        # Safe Mode is selected in the GUI and is persisted for the running scheduler.
        # Its enforcement layer is added separately; this selection does not alter
        # Signal delivery or attempt to evade platform anti-spam controls.
        selected_mode=self.scheduler_mode.get()
        self.storage.set_setting("scheduler_mode",selected_mode)
        self.scheduler=Scheduler(
            msgs,
            self.settings.interval_minutes,
            self.settings.cycle_hours,
            on_state_change=self._scheduler_runtime_state,
            on_post=self._scheduler_post_event,
            on_error=self._scheduler_error_event,
        )
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

    def send_media_now(self):
        if not self.settings.signal_enabled:
            return messagebox.showwarning("Signal", "Enable Signal in Settings before sending.")
        if not self.settings.signal_account:
            return messagebox.showwarning("Signal", "Set or link the Signal account first.")
        groups = self.storage.get_groups(enabled_only=True)
        if not groups:
            return messagebox.showwarning("Signal", "Enable at least one authorized group first.")

        paths = filedialog.askopenfilenames(
            parent=self,
            title="Select 1–3 images or videos to send",
            multiple=True,
            filetypes=[
                ("Images and videos", "*.png *.jpg *.jpeg *.gif *.webp *.bmp *.mp4 *.mov *.webm *.avi *.mkv"),
                ("Image files", "*.png *.jpg *.jpeg *.gif *.webp *.bmp"),
                ("Video files", "*.mp4 *.mov *.webm *.avi *.mkv"),
                ("All files", "*.*"),
            ],
        )
        if isinstance(paths, str):
            paths = (paths,) if paths else ()
        if not paths:
            return

        if len(paths) > 3:
            return messagebox.showwarning(
                "Signal media",
                f"You selected {len(paths)} files. Select between 1 and 3 images/videos.",
            )

        allowed_extensions = {
            ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp",
            ".mp4", ".mov", ".webm", ".avi", ".mkv",
        }
        invalid = [
            path for path in paths
            if os.path.splitext(path)[1].lower() not in allowed_extensions
        ]
        if invalid:
            return messagebox.showwarning(
                "Signal media",
                "Unsupported media type selected:\n" + "\n".join(invalid),
            )

        caption = simpledialog.askstring(
            "Media caption",
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
                f"REAL: sent {len(paths)} media file(s) to {len(groups)} authorized group(s).",
            )
            messagebox.showinfo(
                "Signal",
                f"Sent {len(paths)} media file(s) to {len(groups)} authorized group(s).",
            )
        except Exception as e:
            self.storage.log("ERROR", f"Media send failed: {e}")
            messagebox.showerror("Signal media send", str(e))

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

        toolbar=tk.Frame(self.content,bg=BG)
        toolbar.pack(fill="x",pady=(0,8))

        tk.Button(
            toolbar,text="REFRESH LOGS",command=self._refresh_logs,
            bg=PANEL2,fg=WHITE,padx=14,pady=7,
        ).pack(side="left",padx=(0,5))

        tk.Button(
            toolbar,text="CLEAR LOGS",command=self.clear_logs,
            bg=RED,fg=BG,font=("Segoe UI",9,"bold"),padx=14,pady=7,
        ).pack(side="right")

        self.logs_box=tk.Text(
            self.content,bg="#09100d",fg=WHITE,
            insertbackground=GREEN,wrap="word",
        )
        self.logs_box.pack(fill="both",expand=True)
        self._refresh_logs()

    def _refresh_logs(self):
        if not hasattr(self,"logs_box") or not self.logs_box.winfo_exists():
            return
        self.logs_box.configure(state="normal")
        self.logs_box.delete("1.0","end")
        rows=self.storage.get_logs(500)
        for r in reversed(rows):
            self.logs_box.insert(
                "end",
                f"{r['created_at']} | {r['level']} | {r['message']}\n",
            )
        self.logs_box.configure(state="disabled")

    def clear_logs(self):
        if not messagebox.askyesno(
            "Clear logs",
            "Delete all stored application logs? This cannot be undone.",
            parent=self,
        ):
            return
        try:
            count=self.storage.clear_logs()
            self._refresh_logs()
            messagebox.showinfo(
                "Logs",
                f"Cleared {count} log entr{'y' if count == 1 else 'ies'}.",
                parent=self,
            )
        except Exception as e:
            messagebox.showerror("Logs",str(e),parent=self)

def main():App().mainloop()

if __name__=="__main__":main()
