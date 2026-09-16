"""Local Linux control panel for preparing and reviewing content."""
from __future__ import annotations
import tkinter as tk
from tkinter import messagebox
from .daily_content import generate_variations
from .storage import Storage

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Signal Bot Auto Responder — Review")
        self.geometry("980x760")
        self.storage = Storage()
        self.vars: list[tuple[tk.BooleanVar, tk.Text]] = []

        tk.Label(self, text="Today's message", font=("TkDefaultFont", 12, "bold")).pack(anchor="w", padx=12, pady=(12,4))
        self.source = tk.Text(self, height=4, wrap="word")
        self.source.pack(fill="x", padx=12)

        bar = tk.Frame(self)
        bar.pack(fill="x", padx=12, pady=8)
        tk.Button(bar, text="Generate 24 Variations", command=self.generate).pack(side="left")
        tk.Button(bar, text="Save Approved Pack", command=self.save).pack(side="left", padx=8)

        self.status = tk.Label(bar, text="Ready", anchor="e")
        self.status.pack(side="right")

        self.canvas = tk.Canvas(self)
        scroll = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.frame = tk.Frame(self.canvas)
        self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0,0), window=self.frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scroll.set)
        self.canvas.pack(side="left", fill="both", expand=True, padx=(12,0))
        scroll.pack(side="right", fill="y", padx=(0,12), pady=4)

    def generate(self):
        source = self.source.get("1.0", "end").strip()
        if not source:
            messagebox.showwarning("Missing message", "Enter today's message first.")
            return
        for child in self.frame.winfo_children():
            child.destroy()
        self.vars.clear()
        for i, text in enumerate(generate_variations(source), 1):
            row = tk.Frame(self.frame, pady=4)
            row.pack(fill="x")
            approved = tk.BooleanVar(value=False)
            tk.Checkbutton(row, text=f"{i:02d}", variable=approved).pack(side="left")
            box = tk.Text(row, height=2, wrap="word")
            box.insert("1.0", text)
            box.pack(side="left", fill="x", expand=True)
            self.vars.append((approved, box))
        self.status.config(text="24 variations ready for review")

    def save(self):
        source = self.source.get("1.0", "end").strip()
        if not source or len(self.vars) != 24:
            messagebox.showwarning("Nothing to save", "Generate 24 variations first.")
            return
        approved_text = []
        for approved, box in self.vars:
            if approved.get():
                text = box.get("1.0", "end").strip()
                if text:
                    approved_text.append(text)
        if not approved_text:
            messagebox.showwarning("No approvals", "Approve at least one variation.")
            return
        pack_id = self.storage.save_pack(source, approved_text)
        self.status.config(text=f"Saved pack #{pack_id} ({len(approved_text)} approved)")

def main():
    App().mainloop()

if __name__ == "__main__":
    main()
