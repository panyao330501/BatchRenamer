from __future__ import annotations
from typing import Callable
import customtkinter as ctk


class TopToolbar(ctk.CTkFrame):
    """Top bar: file-loading controls (dialog, folder, wildcard)."""

    def __init__(self, parent: ctk.CTkBaseClass,
                 on_add_files: Callable,
                 on_add_folder: Callable,
                 on_scan: Callable[[str], None]):
        super().__init__(parent, fg_color=("gray82", "#181825"),
                         corner_radius=8, height=46)
        self.pack_propagate(False)
        self._on_scan = on_scan
        self._build(on_add_files, on_add_folder)

    def _build(self, on_add_files: Callable, on_add_folder: Callable) -> None:
        pad = {"padx": 5, "pady": 7}
        btn_kw = {"height": 32, "corner_radius": 6}

        ctk.CTkButton(self, text="+ Add Files", width=100,
                       command=on_add_files, **btn_kw).pack(side="left", **pad)

        ctk.CTkButton(self, text="Add Folder", width=100,
                       command=on_add_folder, **btn_kw).pack(side="left", **pad)

        ctk.CTkLabel(self, text="│", text_color=("gray60", "gray40"),
                      width=10).pack(side="left", padx=2)

        ctk.CTkLabel(self, text="Path / Wildcard:",
                      font=ctk.CTkFont(size=11)).pack(side="left", padx=(4, 0))

        self._path_var = ctk.StringVar()
        entry = ctk.CTkEntry(self, textvariable=self._path_var, width=340,
                              placeholder_text=r"e.g. D:\Downloads\*.jpg",
                              height=32, corner_radius=6)
        entry.pack(side="left", padx=5, pady=7)
        entry.bind("<Return>", lambda _: self._do_scan())

        ctk.CTkButton(self, text="Scan", width=70,
                       command=self._do_scan, **btn_kw).pack(side="left", padx=(0, 5))

        ctk.CTkLabel(self, text="  ↙ Drop files or folders anywhere",
                      text_color=("gray55", "gray50"),
                      font=ctk.CTkFont(size=11)).pack(side="right", padx=12)

    def _do_scan(self) -> None:
        pattern = self._path_var.get().strip()
        if pattern:
            self._on_scan(pattern)


class BottomToolbar(ctk.CTkFrame):
    """Bottom bar: execute, clear, and status message."""

    def __init__(self, parent: ctk.CTkBaseClass,
                 on_execute: Callable,
                 on_clear: Callable):
        super().__init__(parent, fg_color=("gray82", "#181825"),
                         corner_radius=8, height=52)
        self.pack_propagate(False)
        self._build(on_execute, on_clear)

    def _build(self, on_execute: Callable, on_clear: Callable) -> None:
        self._exec_btn = ctk.CTkButton(
            self,
            text="▶  Execute Rename",
            width=170, height=36,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#1e66f5", hover_color="#1a59d6",
            corner_radius=8,
            command=on_execute,
            state="disabled",
        )
        self._exec_btn.pack(side="left", padx=10, pady=8)

        ctk.CTkButton(
            self,
            text="✕  Clear List",
            width=120, height=36,
            fg_color=("gray65", "gray30"), hover_color=("gray55", "gray25"),
            corner_radius=8,
            command=on_clear,
        ).pack(side="left", padx=4, pady=8)

        self._status = ctk.CTkLabel(
            self,
            text="Ready — drag files in or use the buttons above",
            text_color=("gray50", "gray55"),
            font=ctk.CTkFont(size=11),
        )
        self._status.pack(side="left", padx=16)

    def set_status(self, text: str, level: str = "ok") -> None:
        colours = {
            "ok": ("gray50", "gray55"),
            "warning": ("#d97706", "#fbbf24"),
            "error": ("#dc2626", "#f87171"),
        }
        self._status.configure(
            text=text,
            text_color=colours.get(level, colours["ok"]),
        )

    def set_execute_enabled(self, enabled: bool) -> None:
        self._exec_btn.configure(state="normal" if enabled else "disabled")
