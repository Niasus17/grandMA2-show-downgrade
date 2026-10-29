"""Сборка одного exe: python build.py  ->  dist/grandMA2 Show Downgrade.exe (PyInstaller, без консоли)."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onefile", "--windowed",
                "--name", "grandMA2 Show Downgrade", str(ROOT / "app.py")], cwd=ROOT, check=True)
print(ROOT / "dist" / "grandMA2 Show Downgrade.exe")
