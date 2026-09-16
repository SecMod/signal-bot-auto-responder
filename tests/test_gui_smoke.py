import time


def test_gui_end_to_end_smoke(tmp_path, monkeypatch):
    from src.storage import Storage
    from src.gui import App

    monkeypatch.setattr("src.gui.messagebox.showinfo", lambda *a, **k: None)
    monkeypatch.setattr("src.gui.messagebox.showwarning", lambda *a, **k: None)
    monkeypatch.setattr("src.gui.messagebox.showerror", lambda *a, **k: None)

    app = App()
    app.storage = Storage(str(tmp_path / "gui.db"))

    app.source.insert("1.0", "Authorized security assessment")
    app.generate()
    assert len(app.vars) == 24

    app.save_pack()
    assert len(app.storage.list_packs()) == 1

    app.show("packs")
    assert app.storage.list_packs()[0]["approved_count"] == 24

    app.show("groups")
    app.gname.insert(0, "Authorized Group")
    app.gid.insert(0, "group-test")
    app.add_group()
    assert app.storage.get_groups()[0]["group_id"] == "group-test"

    class FakeClient:
        def __init__(self, account, signal_cli="signal-cli"):
            self.account = account

        def list_groups(self):
            return [
                {"name": "Imported A", "group_id": "import-a"},
                {"name": "Imported B", "group_id": "import-b"},
            ]

    monkeypatch.setattr("src.signal_client.SignalClient", FakeClient)
    app.settings = app.settings.__class__(
        interval_minutes=15,
        variation_count=24,
        cycle_hours=6,
        signal_account="+10000000000",
        signal_enabled=False,
        signal_cli_path="signal-cli",
    )
    app.load_groups()
    groups = app.storage.get_groups()
    assert {g["group_id"] for g in groups} == {"group-test", "import-a", "import-b"}
    assert all(g["enabled"] for g in groups if g["group_id"] == "group-test")
    assert all(not g["enabled"] for g in groups if g["group_id"].startswith("import-"))

    app.show("scheduler")
    assert app.pack_choice.get().startswith("#1 | ")
    app.start_scheduler(False)
    assert app.scheduler is not None
    for _ in range(50):
        if not app.scheduler.running:
            break
        time.sleep(0.01)
    app.stop_scheduler()
    assert any("PREVIEW:" in row["message"] for row in app.storage.get_logs())

    app.destroy()
