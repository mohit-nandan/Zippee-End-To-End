def get_screen_size() -> tuple[int, int]:
    """
    Returns (width, height) of the primary display using tkinter (built-in Python).
    Falls back to 1919x1079 if tkinter is unavailable (e.g. headless CI).
    """
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        w, h = root.winfo_screenwidth(), root.winfo_screenheight()
        root.destroy()
        return w, h
    except Exception:
        return 1919, 1079
