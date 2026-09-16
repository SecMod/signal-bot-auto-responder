import threading

from src.storage import Storage


def test_storage_can_log_from_worker_thread(tmp_path):
    storage = Storage(str(tmp_path / "threaded.db"))
    errors = []

    def worker():
        try:
            storage.log("INFO", "worker log")
        except Exception as exc:
            errors.append(exc)

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join()

    assert errors == []
    assert storage.get_logs(1)[0]["message"] == "worker log"
