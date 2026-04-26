from __future__ import annotations
import sys
import os
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES

from core.rules import Rule
from core.rename_engine import compute_new_names
from core.file_loader import load_from_wildcard, parse_drop_paths
from ui.file_panel import FilePanel
from ui.rule_panel import RulePanel
from ui.toolbar import TopToolbar, BottomToolbar

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk, TkinterDnD.DnDWrapper):
    """Main application window.

    Inherits from both CTk (CustomTkinter root) and TkinterDnD.DnDWrapper so
    that drag-and-drop events work alongside the modern CTk theme.
    """

    def __init__(self) -> None:
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        self.title("BatchRenamer")
        self.geometry("1280x720")
        self.minsize(960, 560)

        self._files: list[Path] = []
        self._results: list[dict] = []
        self._debounce_id: str | None = None

        self._build_ui()
        self._setup_drop()

    # --------------------------------------------------------------- layout

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._top_bar = TopToolbar(
            self,
            on_add_files=self._add_files_dialog,
            on_add_folder=self._add_folder_dialog,
            on_scan=self._scan_wildcard,
        )
        self._top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 4))

        # Two-column content area
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=10, pady=4)
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(0, weight=1)

        self._file_panel = FilePanel(content)
        self._file_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 4))

        self._rule_panel = RulePanel(content, on_rules_changed=self._on_rules_changed)
        self._rule_panel.grid(row=0, column=1, sticky="nsew")

        self._bottom_bar = BottomToolbar(
            self,
            on_execute=self._execute,
            on_clear=self._clear_all,
        )
        self._bottom_bar.grid(row=2, column=0, sticky="ew", padx=10, pady=(4, 10))

    # -------------------------------------------------------------- drop

    def _setup_drop(self) -> None:
        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self._on_drop)

    def _on_drop(self, event) -> None:
        paths = parse_drop_paths(event.data, self.tk.splitlist)
        self._add_paths(paths)

    # ---------------------------------------------------------- file loading

    def _add_files_dialog(self) -> None:
        raw = filedialog.askopenfilenames(
            title="Select Files",
            parent=self,
        )
        self._add_paths([Path(p) for p in raw])

    def _add_folder_dialog(self) -> None:
        folder = filedialog.askdirectory(title="Select Folder", parent=self)
        if folder:
            self._add_paths([p for p in Path(folder).iterdir() if p.is_file()])

    def _scan_wildcard(self, pattern: str) -> None:
        paths = load_from_wildcard(pattern)
        if not paths:
            self._bottom_bar.set_status(f"No files matched: {pattern}", "warning")
        self._add_paths(paths)

    def _add_paths(self, paths: list[Path]) -> None:
        existing = {p.resolve() for p in self._files}
        new = [p for p in paths if p.resolve() not in existing]
        self._files.extend(new)
        self._recompute()

    # ----------------------------------------------------------- clear

    def _clear_all(self) -> None:
        self._files.clear()
        self._results.clear()
        self._file_panel.refresh([])
        self._bottom_bar.set_status("List cleared.", "ok")
        self._bottom_bar.set_execute_enabled(False)

    # --------------------------------------------------------- rule change

    def _on_rules_changed(self, rules: list[Rule]) -> None:
        self._rules = rules
        # Debounce so rapid keystrokes don't hammer the engine
        if self._debounce_id is not None:
            self.after_cancel(self._debounce_id)
        self._debounce_id = self.after(100, self._recompute)

    # ------------------------------------------------------ compute preview

    def _recompute(self) -> None:
        rules: list[Rule] = getattr(self, "_rules", [])
        self._results = compute_new_names(self._files, rules)
        self._file_panel.refresh(self._results)
        self._update_status()

    def _update_status(self) -> None:
        n = len(self._files)
        if n == 0:
            self._bottom_bar.set_status("No files loaded.", "ok")
            self._bottom_bar.set_execute_enabled(False)
            return

        rules: list[Rule] = getattr(self, "_rules", [])
        conflicts = sum(1 for r in self._results if r["conflict"])
        errors = sum(1 for r in self._results if r["error"])

        if conflicts:
            self._bottom_bar.set_status(
                f"{n} file(s) — {conflicts} name conflict(s). Resolve before executing.",
                "warning",
            )
            self._bottom_bar.set_execute_enabled(False)
        elif errors:
            self._bottom_bar.set_status(
                f"{n} file(s) — {errors} error(s) in preview. Check rules.",
                "warning",
            )
            self._bottom_bar.set_execute_enabled(False)
        elif not rules:
            self._bottom_bar.set_status(
                f"{n} file(s) loaded — add rules to preview changes.", "ok"
            )
            self._bottom_bar.set_execute_enabled(False)
        else:
            self._bottom_bar.set_status(
                f"{n} file(s) ready to rename.", "ok"
            )
            self._bottom_bar.set_execute_enabled(True)

    # ------------------------------------------------------- execute renames

    def _execute(self) -> None:
        if not self._results:
            return

        success = failed = skipped = 0

        for result in self._results:
            # Skip anything problematic
            if result["error"] or result["conflict"] or result["new_name"] is None:
                skipped += 1
                continue

            src: Path = result["path"]
            dst: Path = src.parent / result["new_name"]

            if src == dst:
                skipped += 1
                continue

            try:
                src.rename(dst)
                result["path"] = dst
                result["original"] = dst.name
                result["status"] = "ok"
                success += 1
            except PermissionError:
                result["status"] = "locked"
                result["error"] = "File in use"
                failed += 1
            except Exception as exc:
                result["status"] = "error"
                result["error"] = str(exc)
                failed += 1

        # Refresh files list to reflect renamed paths
        self._files = [r["path"] for r in self._results]
        self._file_panel.refresh(self._results)

        level = "ok" if failed == 0 else "warning"
        self._bottom_bar.set_status(
            f"Done — {success} renamed, {failed} failed, {skipped} skipped.",
            level,
        )
        self._bottom_bar.set_execute_enabled(False)
