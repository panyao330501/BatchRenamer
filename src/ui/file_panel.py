import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

_COLUMNS = ("original", "new_name", "status")
_HEADINGS = ("Original Name", "New Name", "Status")
_WIDTHS = (310, 310, 130)


class FilePanel(ctk.CTkFrame):
    """Left panel: a styled Treeview showing original/new/status per file."""

    def __init__(self, parent: tk.Widget):
        super().__init__(parent)
        self._build()

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ctk.CTkLabel(self, text="Files",
                               font=ctk.CTkFont(size=14, weight="bold"))
        header.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))

        self._apply_style()

        # Treeview container (plain tk.Frame so bg colour matches)
        tree_container = tk.Frame(self, bg="#1e1e2e")
        tree_container.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
        tree_container.columnconfigure(0, weight=1)
        tree_container.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            tree_container,
            columns=_COLUMNS,
            show="headings",
            selectmode="extended",
            style="BR.Treeview",
        )
        for col, heading, width in zip(_COLUMNS, _HEADINGS, _WIDTHS):
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, minwidth=60, stretch=True)

        vsb = ttk.Scrollbar(tree_container, orient="vertical",
                             command=self.tree.yview, style="BR.Vertical.TScrollbar")
        hsb = ttk.Scrollbar(tree_container, orient="horizontal",
                             command=self.tree.xview, style="BR.Horizontal.TScrollbar")
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Row colour tags
        self.tree.tag_configure("conflict", foreground="#ff6b6b")
        self.tree.tag_configure("error", foreground="#ffa94d")
        self.tree.tag_configure("done", foreground="#69db7c")
        self.tree.tag_configure("normal", foreground="#cdd6f4")
        self.tree.tag_configure("unchanged", foreground="#6c7086")

    @staticmethod
    def _apply_style() -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        bg = "#1e1e2e"
        fg = "#cdd6f4"
        sel_bg = "#313244"
        head_bg = "#181825"
        head_fg = "#a6adc8"

        style.configure("BR.Treeview",
                         background=bg, foreground=fg,
                         fieldbackground=bg, borderwidth=0,
                         rowheight=26, font=("Segoe UI", 10))
        style.configure("BR.Treeview.Heading",
                         background=head_bg, foreground=head_fg,
                         borderwidth=0, relief="flat",
                         font=("Segoe UI", 10, "bold"))
        style.map("BR.Treeview",
                  background=[("selected", sel_bg)],
                  foreground=[("selected", fg)])
        style.configure("BR.Vertical.TScrollbar",
                         background="#313244", troughcolor=bg,
                         borderwidth=0, arrowsize=12)
        style.configure("BR.Horizontal.TScrollbar",
                         background="#313244", troughcolor=bg,
                         borderwidth=0, arrowsize=12)

    def refresh(self, results: list[dict]) -> None:
        """Rebuild the table from a fresh results list."""
        self.tree.delete(*self.tree.get_children())
        for r in results:
            original = r["original"]
            status_text = ""

            if r.get("status") == "ok":
                new_name = r["new_name"] or original
                status_text = "Done ✓"
                tag = "done"
            elif r.get("status") in ("locked", "error"):
                new_name = r.get("new_name") or ""
                status_text = f"Failed: {r.get('error', '')}"
                tag = "error"
            elif r["error"]:
                new_name = f"[ERR] {r['error']}"
                status_text = "Error"
                tag = "error"
            elif r["conflict"]:
                new_name = r["new_name"] or ""
                status_text = "Conflict !"
                tag = "conflict"
            else:
                new_name = r["new_name"] or original
                status_text = ""
                tag = "unchanged" if new_name == original else "normal"

            self.tree.insert("", "end",
                              values=(original, new_name, status_text),
                              tags=(tag,))
