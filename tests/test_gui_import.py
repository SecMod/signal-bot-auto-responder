def test_gui_module_imports():
    from src.gui import App
    assert App.__name__ == "App"
