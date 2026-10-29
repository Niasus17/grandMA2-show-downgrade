"""grandMA2 Show Downgrade — open a grandMA2 3.9.x show file in an OLDER 3.9 version.

Pick a .show.gz, see its version, choose a lower 3.9 version, convert. The original file is not changed; the new file is
saved as «name (3.9.60.45).show.gz» into that version's onPC shows folder if it is installed, or next to the original.
Перевод шоу grandMA2 3.9.x в более старую версию 3.9: выбрать шоу, выбрать версию ниже — готово.
"""
from __future__ import annotations

import os
import re
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import showconv as C

APP = "grandMA2 Show Downgrade"
VERSION = "1.0"
MA_BASE = Path(os.environ.get("ProgramData", "C:/ProgramData")) / "MA Lighting Technologies" / "grandma"
T = {   # RU / EN
    "pick": ("Выбрать шоу…", "Choose show…"),
    "none": ("Шоу не выбрано", "No show selected"),
    "ver": ("Версия шоу: {v}", "Show version: {v}"),
    "to": ("Перевести под версию (только младше — новая MA откроет шоу и так):",
           "Convert to version (lower only — a newer MA opens the show anyway):"),
    "other": ("Другая версия:", "Other version:"),
    "go": ("Перевести", "Convert"),
    "inst": ("установлена", "installed"),
    "ok_t": ("Готово", "Done"),
    "ok": ("Сохранено:\n{p}\n\nИсходное шоу не изменено.", "Saved:\n{p}\n\nThe original show is unchanged."),
    "err": ("Ошибка", "Error"),
    "nolow": ("Известных версий младше этой нет — введите версию вручную.", "No known lower version — type one."),
    "note": ("Проверено: 3.9.61.5 и 3.9.63.11 → 3.9.60.45. Шоу с функциями только новой версии не проверялись.",
             "Verified: 3.9.61.5 and 3.9.63.11 → 3.9.60.45. Shows using features of the newer version are untested."),
    "lang": ("English", "Русский"),
}


def ui_lang_ru() -> bool:
    try:
        import ctypes
        return ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3FF == 0x19
    except Exception:
        return False


def installed() -> dict[str, Path]:
    out = {}
    try:
        for d in MA_BASE.iterdir():
            m = re.match(r"^gma2_V_([\d.]+)$", d.name, re.I)
            if m and (d / "shows").exists():
                out[m.group(1)] = d / "shows"
    except OSError:
        pass
    return out


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.lang = 0 if ui_lang_ru() else 1                 # язык Windows русский — по-русски, иначе по-английски
        self.title(f"{APP} {VERSION}")
        self.geometry("620x470")
        self.minsize(520, 420)
        self.src: Path | None = None
        self.ver: tuple | None = None
        self.target = tk.StringVar()
        self.custom = tk.StringVar()
        self._build()

    def t(self, k: str, **kw) -> str:
        return T[k][self.lang].format(**kw)

    def _build(self) -> None:
        for w in self.winfo_children():
            w.destroy()
        pad = {"padx": 12, "pady": 6}
        top = ttk.Frame(self)
        top.pack(fill="x", **pad)
        ttk.Button(top, text=self.t("pick"), command=self.pick).pack(side="left")
        ttk.Button(top, text=self.t("lang"), command=self.toggle_lang).pack(side="right")
        self.lbl = ttk.Label(self, text=self.t("none"), wraplength=580, justify="left")
        self.lbl.pack(fill="x", **pad)
        self.box = ttk.Frame(self)
        self.box.pack(fill="both", expand=True, **pad)
        ttk.Label(self, text=self.t("note"), wraplength=580, foreground="#666").pack(fill="x", padx=12, pady=(0, 10))
        self._targets()

    def toggle_lang(self) -> None:
        self.lang = 1 - self.lang
        self._build()
        if self.src:
            self._show_src()

    def pick(self) -> None:
        start = MA_BASE if MA_BASE.exists() else Path.home()
        p = filedialog.askopenfilename(title=self.t("pick"), initialdir=str(start),
                                       filetypes=[("grandMA2 show", "*.show.gz"), ("*", "*.*")])
        if not p:
            return
        try:
            self.ver = C.read_version(p)
        except Exception as e:
            messagebox.showerror(self.t("err"), str(e))
            return
        self.src = Path(p)
        self._show_src()

    def _show_src(self) -> None:
        self.lbl.config(text=f"{self.src.name}\n{self.t('ver', v=C.ver_str(self.ver))}")
        self._targets()

    def _targets(self) -> None:
        for w in self.box.winfo_children():
            w.destroy()
        if not self.ver:
            return
        inst = installed()
        ttk.Label(self.box, text=self.t("to"), wraplength=580).pack(anchor="w")
        lst = C.targets(self.ver)
        if not lst:
            ttk.Label(self.box, text=self.t("nolow")).pack(anchor="w", pady=4)
        grid = ttk.Frame(self.box)
        grid.pack(fill="x", pady=4)
        for i, v in enumerate(lst):
            rel = ".".join(v.split(".")[:3])
            txt = v + (f"  ({self.t('inst')})" if rel in inst else "") + ("  ✓" if v in C.VERIFIED else "")
            ttk.Radiobutton(grid, text=txt, value=v, variable=self.target).grid(row=i // 2, column=i % 2, sticky="w", padx=4, pady=2)
        if lst and self.target.get() not in lst:
            self.target.set(lst[0])
        row = ttk.Frame(self.box)
        row.pack(fill="x", pady=6)
        ttk.Label(row, text=self.t("other")).pack(side="left")
        ttk.Entry(row, textvariable=self.custom, width=14).pack(side="left", padx=6)
        ttk.Button(self.box, text=self.t("go"), command=self.go).pack(anchor="w", pady=8)

    def go(self) -> None:
        v = self.custom.get().strip() or self.target.get()
        if not (self.src and v):
            return
        try:
            t = C.parse_ver(v)
            d = installed().get(f"{t[0]}.{t[1]}.{t[2]}")
            stem = self.src.name[:-8] if self.src.name.lower().endswith(".show.gz") else self.src.stem
            out = C.convert(self.src, v, (d or self.src.parent) / f"{stem} ({v}).show.gz")
        except Exception as e:
            messagebox.showerror(self.t("err"), str(e))
            return
        messagebox.showinfo(self.t("ok_t"), self.t("ok", p=out))


def cli(argv: list[str]) -> int:
    """Без окна: app.exe <шоу.show.gz> <версия> [куда.show.gz]."""
    out = C.convert(argv[0], argv[1], argv[2] if len(argv) > 2 else None)
    print(out)
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 2:
        sys.exit(cli(sys.argv[1:]))
    App().mainloop()
