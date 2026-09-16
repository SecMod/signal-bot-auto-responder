"""Desktop control panel for message preparation and authorized groups."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from .config import Settings
from .daily_content import generate_variations
from .storage import Storage


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Signal Bot Auto Responder - Review")
        self.geometry("1100x850")
        self.minsize(900, 700)

        self.storage = Storage()
        self.settings = Settings.from_env()

        self.vars: list[tuple[tk.BooleanVar, tk.Text]] = []
        self.group_vars: dict[str, tk.BooleanVar] = {}

        self._build_header()
        self._build_source()
        self._build_controls()
        self._build_groups()
        self._build_variations()
        self._build_footer()

        self.refresh_groups()

    def _build_header(self) -> None:
        tk.Label(
            self,
            text="SIGNAL BOT AUTO RESPONDER",
            font=("TkDefaultFont", 16, "bold"),
        ).pack(anchor="w", padx=15, pady=(15, 2))

        tk.Label(
            self,
            text="Daily message preparation and authorized group configuration",
        ).pack(anchor="w", padx=15, pady=(0, 10))

    def _build_source(self) -> None:
        tk.Label(
            self,
            text="Today's message",
            font=("TkDefaultFont", 12, "bold"),
        ).pack(anchor="w", padx=15, pady=(5, 4))

        self.source = tk.Text(
            self,
            height=4,
            wrap="word",
        )
        self.source.pack(fill="x", padx=15)

    def _build_controls(self) -> None:
        bar = tk.Frame(self)
        bar.pack(fill="x", padx=15, pady=10)

        tk.Button(
            bar,
            text="Generate 24 Variations",
            command=self.generate,
        ).pack(side="left")

        tk.Button(
            bar,
            text="Select All",
            command=self.select_all,
        ).pack(side="left", padx=5)

        tk.Button(
            bar,
            text="Deselect All",
            command=self.deselect_all,
        ).pack(side="left", padx=5)

        tk.Button(
            bar,
            text="Save Approved Pack",
            command=self.save,
        ).pack(side="left", padx=5)

        self.status = tk.Label(
            bar,
            text="Ready",
            anchor="e",
        )
        self.status.pack(side="right")

    def _build_groups(self) -> None:
        outer = tk.LabelFrame(
            self,
            text="Authorized Signal Groups",
            padx=10,
            pady=8,
        )
        outer.pack(
            fill="x",
            padx=15,
            pady=(0, 10),
        )

        form = tk.Frame(outer)
        form.pack(fill="x")

        tk.Label(
            form,
            text="Name:",
        ).pack(side="left")

        self.group_name = tk.Entry(
            form,
            width=22,
        )
        self.group_name.pack(
            side="left",
            padx=(5, 15),
        )

        tk.Label(
            form,
            text="Group ID:",
        ).pack(side="left")

        self.group_id = tk.Entry(
            form,
            width=35,
        )
        self.group_id.pack(
            side="left",
            padx=5,
        )

        tk.Button(
            form,
            text="Add Group",
            command=self.add_group,
        ).pack(
            side="left",
            padx=5,
        )

        tk.Button(
            form,
            text="Remove Selected",
            command=self.remove_selected_groups,
        ).pack(
            side="left",
            padx=5,
        )

        self.groups_frame = tk.Frame(outer)
        self.groups_frame.pack(
            fill="x",
            pady=(8, 0),
        )

    def _build_variations(self) -> None:
        tk.Label(
            self,
            text="Message variations",
            font=("TkDefaultFont", 12, "bold"),
        ).pack(anchor="w", padx=15)

        container = tk.Frame(self)
        container.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(5, 10),
        )

        self.canvas = tk.Canvas(container)

        scroll = tk.Scrollbar(
            container,
            orient="vertical",
            command=self.canvas.yview,
        )

        self.frame = tk.Frame(self.canvas)

        self.frame.bind(
            "<Configure>",
            lambda event: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            ),
        )

        self.canvas.create_window(
            (0, 0),
            window=self.frame,
            anchor="nw",
        )

        self.canvas.configure(
            yscrollcommand=scroll.set,
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True,
        )

        scroll.pack(
            side="right",
            fill="y",
        )

    def _build_footer(self) -> None:
        footer = tk.Frame(self)
        footer.pack(
            fill="x",
            padx=15,
            pady=(0, 15),
        )

        tk.Label(
            footer,
            text=(
                f"Interval: {self.settings.interval_minutes} minutes   |   "
                f"Cycle: {self.settings.cycle_hours} hours   |   "
                f"Variations: {self.settings.variation_count}"
            ),
        ).pack(side="left")

    def refresh_groups(self) -> None:
        for child in self.groups_frame.winfo_children():
            child.destroy()

        self.group_vars.clear()

        groups = self.storage.get_groups()

        if not groups:
            tk.Label(
                self.groups_frame,
                text="No groups configured.",
            ).pack(anchor="w")

            return

        for group in groups:
            row = tk.Frame(self.groups_frame)
            row.pack(
                fill="x",
                pady=2,
            )

            enabled = tk.BooleanVar(
                value=group["enabled"]
            )

            self.group_vars[group["group_id"]] = enabled

            tk.Checkbutton(
                row,
                text=group["name"],
                variable=enabled,
                command=lambda gid=group["group_id"], var=enabled:
                    self.toggle_group(gid, var),
            ).pack(side="left")

            tk.Label(
                row,
                text=f"ID: {group['group_id']}",
            ).pack(
                side="left",
                padx=10,
            )

            state = "Enabled" if group["enabled"] else "Disabled"

            tk.Label(
                row,
                text=state,
            ).pack(side="right")

    def add_group(self) -> None:
        name = self.group_name.get().strip()
        group_id = self.group_id.get().strip()

        if not name or not group_id:
            messagebox.showwarning(
                "Missing information",
                "Enter both a group name and group ID.",
            )
            return

        try:
            self.storage.add_group(
                name,
                group_id,
            )
        except Exception as exc:
            messagebox.showerror(
                "Could not add group",
                str(exc),
            )
            return

        self.group_name.delete(0, "end")
        self.group_id.delete(0, "end")

        self.refresh_groups()

        self.status.config(
            text=f"Added group: {name}"
        )

    def toggle_group(
        self,
        group_id: str,
        variable: tk.BooleanVar,
    ) -> None:
        enabled = variable.get()

        self.storage.set_group_enabled(
            group_id,
            enabled,
        )

        self.status.config(
            text=(
                f"Group {'enabled' if enabled else 'disabled'}: "
                f"{group_id}"
            )
        )

        self.refresh_groups()

    def remove_selected_groups(self) -> None:
        selected = [
            group_id
            for group_id, variable in self.group_vars.items()
            if not variable.get()
        ]

        if not selected:
            messagebox.showinfo(
                "Nothing selected",
                "Uncheck the groups you want to remove.",
            )
            return

        if not messagebox.askyesno(
            "Confirm removal",
            f"Remove {len(selected)} disabled group(s)?",
        ):
            return

        for group_id in selected:
            self.storage.remove_group(group_id)

        self.refresh_groups()

        self.status.config(
            text=f"Removed {len(selected)} group(s)"
        )

    def generate(self) -> None:
        source = self.source.get(
            "1.0",
            "end",
        ).strip()

        if not source:
            messagebox.showwarning(
                "Missing message",
                "Enter today's message first.",
            )
            return

        for child in self.frame.winfo_children():
            child.destroy()

        self.vars.clear()

        variations = generate_variations(
            source,
            self.settings.variation_count,
        )

        for number, message in enumerate(
            variations,
            1,
        ):
            row = tk.Frame(
                self.frame,
                pady=4,
            )
            row.pack(
                fill="x",
                padx=5,
            )

            approved = tk.BooleanVar(
                value=True
            )

            tk.Checkbutton(
                row,
                text=f"{number:02d}",
                variable=approved,
            ).pack(side="left")

            box = tk.Text(
                row,
                height=2,
                wrap="word",
            )

            box.insert(
                "1.0",
                message,
            )

            box.pack(
                side="left",
                fill="x",
                expand=True,
            )

            self.vars.append(
                (approved, box)
            )

        self.status.config(
            text="24 variations ready for review"
        )

    def select_all(self) -> None:
        for approved, _ in self.vars:
            approved.set(True)

    def deselect_all(self) -> None:
        for approved, _ in self.vars:
            approved.set(False)

    def save(self) -> None:
        source = self.source.get(
            "1.0",
            "end",
        ).strip()

        if not source or len(self.vars) != 24:
            messagebox.showwarning(
                "Nothing to save",
                "Generate 24 variations first.",
            )
            return

        approved_text: list[str] = []

        for approved, box in self.vars:
            if approved.get():
                text = box.get(
                    "1.0",
                    "end",
                ).strip()

                if text:
                    approved_text.append(text)

        if len(approved_text) != 24:
            messagebox.showwarning(
                "24 approvals required",
                "Approve all 24 variations before saving.",
            )
            return

        pack_id = self.storage.save_pack(
            source,
            approved_text,
        )

        self.status.config(
            text=f"Saved pack #{pack_id} - 24 variations"
        )

        messagebox.showinfo(
            "Saved",
            "Today's 24-message pack has been saved.",
        )


def main() -> None:
    App().mainloop()


if __name__ == "__main__":
    main()
