from __future__ import annotations
import tkinter as tk
from typing import Callable
import customtkinter as ctk

from core.rules import (
    Rule, ChangeExtRule, SerializeRule, SliceKeepRule,
    SliceDeleteRule, InsertRule, FullRenameRule,
    ClearChineseRule, DeleteStringRule,
)

_RULE_LABELS: dict[str, str] = {
    "extension":    "Change Extension",
    "serialize":    "Serialize (Number)",
    "slice_keep":   "Keep Characters",
    "slice_delete":  "Delete Characters",
    "insert":       "Insert Text",
    "full_rename":  "Full Rename",
    "clear_chinese": "Clear Chinese",
    "delete_string": "Delete String",
}

_RULE_FACTORIES: dict[str, type[Rule]] = {
    "extension":    ChangeExtRule,
    "serialize":    SerializeRule,
    "slice_keep":   SliceKeepRule,
    "slice_delete":  SliceDeleteRule,
    "insert":       InsertRule,
    "full_rename":  FullRenameRule,
    "clear_chinese": ClearChineseRule,
    "delete_string": DeleteStringRule,
}


class RulePanel(ctk.CTkFrame):
    """Right panel: a scrollable list of rule cards."""

    def __init__(self, parent: tk.Widget, on_rules_changed: Callable[[list[Rule]], None]):
        super().__init__(parent)
        self._on_rules_changed = on_rules_changed
        self._cards: list[RuleCard] = []
        self._build()

    # ------------------------------------------------------------------ build

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Header row
        header_row = ctk.CTkFrame(self, fg_color="transparent")
        header_row.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 4))
        header_row.columnconfigure(0, weight=1)

        ctk.CTkLabel(header_row, text="Rules",
                      font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w")

        self._add_btn = ctk.CTkButton(
            header_row, text="+ Add Rule", width=115, height=32,
            corner_radius=6, command=self._show_add_menu,
        )
        self._add_btn.grid(row=0, column=1, sticky="e")

        # Scrollable card area
        self._scroll = ctk.CTkScrollableFrame(self, fg_color=("gray88", "#13131f"),
                                               corner_radius=6)
        self._scroll.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
        self._scroll.columnconfigure(0, weight=1)

        self._placeholder = ctk.CTkLabel(
            self._scroll,
            text="No rules yet.\nClick '+ Add Rule' to start.",
            text_color=("gray55", "gray45"),
            font=ctk.CTkFont(size=12),
            justify="center",
        )
        self._placeholder.grid(row=0, column=0, pady=50)

    # ------------------------------------------------------- add-rule popup

    def _show_add_menu(self) -> None:
        popup = ctk.CTkToplevel(self)
        popup.title("Add Rule")
        popup.geometry("230x310")
        popup.resizable(False, False)
        popup.attributes("-topmost", True)

        # Position below the add button
        self._add_btn.update_idletasks()
        bx = self._add_btn.winfo_rootx()
        by = self._add_btn.winfo_rooty() + self._add_btn.winfo_height() + 4
        popup.geometry(f"+{bx}+{by}")

        ctk.CTkLabel(popup, text="Select Rule Type",
                      font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(12, 8))

        for rule_type, label in _RULE_LABELS.items():
            def _make_cmd(rt: str = rule_type) -> Callable:
                def cmd() -> None:
                    popup.destroy()
                    self._add_rule(rt)
                return cmd

            ctk.CTkButton(
                popup, text=label, anchor="w",
                height=30, corner_radius=4,
                fg_color="transparent",
                hover_color=("gray75", "#313244"),
                text_color=("gray10", "gray90"),
                command=_make_cmd(),
            ).pack(fill="x", padx=14, pady=2)

    # --------------------------------------------------------- card lifecycle

    def _add_rule(self, rule_type: str) -> None:
        rule = _RULE_FACTORIES[rule_type]()
        card = RuleCard(
            self._scroll, rule=rule,
            on_change=self._emit,
            on_delete=self._remove_card,
        )
        card.grid(row=len(self._cards), column=0, sticky="ew", padx=4, pady=3)
        self._cards.append(card)
        self._placeholder.grid_remove()
        self._emit()

    def _remove_card(self, card: RuleCard) -> None:
        card.destroy()
        self._cards.remove(card)
        for i, c in enumerate(self._cards):
            c.grid(row=i, column=0, sticky="ew", padx=4, pady=3)
        if not self._cards:
            self._placeholder.grid(row=0, column=0, pady=50)
        self._emit()

    def _emit(self) -> None:
        rules = [c.get_rule() for c in self._cards]
        self._on_rules_changed(rules)


# ======================================================================= card

class RuleCard(ctk.CTkFrame):
    """A collapsible card representing one rename rule with its parameter widgets."""

    def __init__(self, parent: tk.Widget, rule: Rule,
                 on_change: Callable, on_delete: Callable[[RuleCard], None]):
        super().__init__(parent, border_width=1,
                          border_color=("gray70", "#313244"),
                          corner_radius=8, fg_color=("gray90", "#1e1e2e"))
        self._rule = rule
        self._on_change = on_change
        self._on_delete = on_delete
        self._build()

    # --------------------------------------------------------------- build UI

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)

        # ---- title bar ----
        title_bar = ctk.CTkFrame(self, fg_color=("gray80", "#181825"),
                                  corner_radius=6)
        title_bar.grid(row=0, column=0, sticky="ew", padx=3, pady=3)
        title_bar.columnconfigure(0, weight=1)

        label_text = _RULE_LABELS.get(self._rule.rule_type, self._rule.rule_type)
        ctk.CTkLabel(title_bar, text=label_text,
                      font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=5)

        ctk.CTkButton(
            title_bar, text="✕", width=26, height=22,
            fg_color="transparent", hover_color=("#ffb3b3", "#7f1d1d"),
            text_color=("gray40", "gray60"),
            command=lambda: self._on_delete(self),
        ).grid(row=0, column=1, padx=6, pady=3)

        # ---- parameter area ----
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="ew", padx=10, pady=(2, 10))
        content.columnconfigure(1, weight=1)

        self._build_content(content)

    def _build_content(self, f: ctk.CTkFrame) -> None:
        rt = self._rule.rule_type
        dispatch = {
            "extension":    self._build_extension,
            "serialize":    self._build_serialize,
            "slice_keep":   self._build_slice_keep,
            "slice_delete":  self._build_slice_delete,
            "insert":       self._build_insert,
            "full_rename":  self._build_full_rename,
            "clear_chinese": self._build_clear_chinese,
            "delete_string": self._build_delete_string,
        }
        builder = dispatch.get(rt)
        if builder:
            builder(f)

    # ------------------------------------------------------- per-rule widgets

    def _lbl(self, f: ctk.CTkFrame, text: str, row: int, col: int = 0) -> None:
        ctk.CTkLabel(f, text=text, font=ctk.CTkFont(size=11),
                      anchor="w").grid(row=row, column=col, sticky="w", pady=2)

    def _hint(self, f: ctk.CTkFrame, text: str, row: int, col: int = 2) -> None:
        ctk.CTkLabel(f, text=text, text_color=("gray55", "gray50"),
                      font=ctk.CTkFont(size=10)).grid(
            row=row, column=col, sticky="w", padx=(4, 0))

    # — Extension —
    def _build_extension(self, f: ctk.CTkFrame) -> None:
        self._lbl(f, "Mode:", 0)
        self._ext_mode = tk.StringVar(value=self._rule.mode)
        cb = ctk.CTkComboBox(
            f, values=["replace", "add", "remove"],
            variable=self._ext_mode, width=110,
            command=lambda _: self._on_ext_mode_change(),
        )
        cb.grid(row=0, column=1, sticky="w", padx=6, pady=2)

        self._lbl(f, "Extension:", 1)
        self._ext_val = tk.StringVar(value=self._rule.new_ext)
        self._ext_entry = ctk.CTkEntry(f, textvariable=self._ext_val,
                                        width=100, placeholder_text=".jpg")
        self._ext_entry.grid(row=1, column=1, sticky="w", padx=6, pady=2)
        self._ext_val.trace_add("write", lambda *_: self._emit())
        self._on_ext_mode_change()

    def _on_ext_mode_change(self) -> None:
        mode = self._ext_mode.get()
        state = "normal" if mode in ("replace", "add") else "disabled"
        self._ext_entry.configure(state=state)
        self._emit()

    # — Serialize —
    def _build_serialize(self, f: ctk.CTkFrame) -> None:
        self._lbl(f, "Pattern:", 0)
        self._ser_pattern = tk.StringVar(value=self._rule.pattern)
        ctk.CTkEntry(f, textvariable=self._ser_pattern, width=100,
                      placeholder_text="# or file_#").grid(
            row=0, column=1, sticky="w", padx=6, pady=2)
        self._hint(f, "# = number placeholder", 0)
        self._ser_pattern.trace_add("write", lambda *_: self._emit())

        self._lbl(f, "Start at:", 1)
        self._ser_start = tk.StringVar(value=str(self._rule.start))
        ctk.CTkEntry(f, textvariable=self._ser_start, width=60).grid(
            row=1, column=1, sticky="w", padx=6, pady=2)
        self._ser_start.trace_add("write", lambda *_: self._emit())

        self._lbl(f, "Padding:", 2)
        pad_frame = ctk.CTkFrame(f, fg_color="transparent")
        pad_frame.grid(row=2, column=1, sticky="w", pady=2)
        self._ser_auto = tk.BooleanVar(value=(self._rule.padding == 0))
        self._pad_cb = ctk.CTkCheckBox(pad_frame, text="Auto",
                                        variable=self._ser_auto,
                                        command=self._on_pad_toggle,
                                        width=60)
        self._pad_cb.pack(side="left")
        self._ser_pad = tk.StringVar(value=str(self._rule.padding or ""))
        self._pad_entry = ctk.CTkEntry(pad_frame, textvariable=self._ser_pad, width=50)
        self._pad_entry.pack(side="left", padx=4)
        self._ser_pad.trace_add("write", lambda *_: self._emit())
        self._on_pad_toggle()

    def _on_pad_toggle(self) -> None:
        is_auto = self._ser_auto.get()
        self._pad_entry.configure(state="disabled" if is_auto else "normal")
        self._emit()

    # — SliceKeep —
    def _build_slice_keep(self, f: ctk.CTkFrame) -> None:
        self._lbl(f, "From char:", 0)
        self._sk_n = tk.StringVar(value=str(self._rule.n))
        ctk.CTkEntry(f, textvariable=self._sk_n, width=60).grid(
            row=0, column=1, sticky="w", padx=6, pady=2)
        self._hint(f, "1-indexed", 0)
        self._sk_n.trace_add("write", lambda *_: self._emit())

        self._lbl(f, "To char:", 1)
        self._sk_m = tk.StringVar(value=str(self._rule.m))
        ctk.CTkEntry(f, textvariable=self._sk_m, width=60).grid(
            row=1, column=1, sticky="w", padx=6, pady=2)
        self._hint(f, "-1 = end", 1)
        self._sk_m.trace_add("write", lambda *_: self._emit())

    # — SliceDelete —
    def _build_slice_delete(self, f: ctk.CTkFrame) -> None:
        self._lbl(f, "From char:", 0)
        self._sd_n = tk.StringVar(value=str(self._rule.n))
        ctk.CTkEntry(f, textvariable=self._sd_n, width=60).grid(
            row=0, column=1, sticky="w", padx=6, pady=2)
        self._hint(f, "1-indexed", 0)
        self._sd_n.trace_add("write", lambda *_: self._emit())

        self._lbl(f, "To char:", 1)
        self._sd_m = tk.StringVar(value=str(self._rule.m))
        ctk.CTkEntry(f, textvariable=self._sd_m, width=60).grid(
            row=1, column=1, sticky="w", padx=6, pady=2)
        self._sd_m.trace_add("write", lambda *_: self._emit())

    # — Insert —
    def _build_insert(self, f: ctk.CTkFrame) -> None:
        self._lbl(f, "Text:", 0)
        self._ins_text = tk.StringVar(value=self._rule.text)
        ctk.CTkEntry(f, textvariable=self._ins_text, width=160).grid(
            row=0, column=1, sticky="w", padx=6, pady=2)
        self._ins_text.trace_add("write", lambda *_: self._emit())

        self._lbl(f, "Position:", 1)
        self._ins_pos = tk.StringVar(value=str(self._rule.pos))
        ctk.CTkEntry(f, textvariable=self._ins_pos, width=60).grid(
            row=1, column=1, sticky="w", padx=6, pady=2)
        self._hint(f, "0=prepend  −1=append", 1)
        self._ins_pos.trace_add("write", lambda *_: self._emit())

    # — FullRename —
    def _build_full_rename(self, f: ctk.CTkFrame) -> None:
        self._lbl(f, "Name:", 0)
        self._fr_name = tk.StringVar(value=self._rule.name)
        ctk.CTkEntry(f, textvariable=self._fr_name, width=160).grid(
            row=0, column=1, sticky="w", padx=6, pady=2)
        self._fr_name.trace_add("write", lambda *_: self._emit())

        ctk.CTkLabel(
            f, text="⚠  Also add a Serialize rule to avoid conflicts",
            text_color=("#b45309", "#fbbf24"),
            font=ctk.CTkFont(size=10),
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 0))

    # — ClearChinese —
    def _build_clear_chinese(self, f: ctk.CTkFrame) -> None:
        ctk.CTkLabel(
            f,
            text="Removes all CJK Unified Ideograph characters\nfrom the filename stem.",
            text_color=("gray50", "gray55"),
            font=ctk.CTkFont(size=10),
            justify="left",
        ).grid(row=0, column=0, columnspan=3, sticky="w")

    # — DeleteString —
    def _build_delete_string(self, f: ctk.CTkFrame) -> None:
        self._lbl(f, "String:", 0)
        self._ds_target = tk.StringVar(value=self._rule.target)
        ctk.CTkEntry(f, textvariable=self._ds_target, width=160,
                      placeholder_text="text to remove").grid(
            row=0, column=1, sticky="w", padx=6, pady=2)
        self._ds_target.trace_add("write", lambda *_: self._emit())

    # ---------------------------------------------------- emit / get_rule

    def _emit(self) -> None:
        self._on_change()

    def _int(self, var: tk.StringVar, default: int) -> int:
        try:
            return int(var.get())
        except (ValueError, tk.TclError):
            return default

    def get_rule(self) -> Rule:
        rt = self._rule.rule_type
        try:
            if rt == "extension":
                return ChangeExtRule(mode=self._ext_mode.get(),
                                      new_ext=self._ext_val.get())
            if rt == "serialize":
                pad = 0 if self._ser_auto.get() else self._int(self._ser_pad, 0)
                return SerializeRule(
                    pattern=self._ser_pattern.get() or "#",
                    start=self._int(self._ser_start, 1),
                    padding=pad,
                )
            if rt == "slice_keep":
                return SliceKeepRule(n=self._int(self._sk_n, 1),
                                      m=self._int(self._sk_m, -1))
            if rt == "slice_delete":
                return SliceDeleteRule(n=self._int(self._sd_n, 1),
                                        m=self._int(self._sd_m, 1))
            if rt == "insert":
                return InsertRule(text=self._ins_text.get(),
                                   pos=self._int(self._ins_pos, 0))
            if rt == "full_rename":
                return FullRenameRule(name=self._fr_name.get() or "file")
            if rt == "clear_chinese":
                return ClearChineseRule()
            if rt == "delete_string":
                return DeleteStringRule(target=self._ds_target.get())
        except Exception:
            pass
        return self._rule
