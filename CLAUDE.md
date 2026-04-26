# BatchRenamer

A modern Windows desktop application for batch file renaming with multi-rule pipelines, real-time preview, and drag-and-drop support.

## Conda Environment

```
Name: rename
Path: C:\Users\A\miniconda3\envs\rename
```

Activate:
```bash
conda activate rename
```

## Dev Setup

```bash
conda activate rename
pip install -r requirements.txt
```

Run the app:
```bash
python src/main.py
```

## Project Structure

```
src/
├── main.py               # Entry point
├── app.py                # Main CTk window + state management
├── ui/
│   ├── file_panel.py     # File list Treeview (Original / New / Status columns)
│   ├── rule_panel.py     # Scrollable rule cards (add/remove rules)
│   └── toolbar.py        # Top file-loading toolbar + bottom execute toolbar
├── core/
│   ├── rules.py          # Rule dataclasses with apply() method
│   ├── rename_engine.py  # Pipeline: apply rules in order, detect conflicts
│   └── file_loader.py    # Dialog, wildcard glob, drag-drop parsing
└── utils/
    └── validators.py     # Guard checks (FullRename without Serialize, etc.)
```

## Build

```bash
conda activate rename
pyinstaller batch_renamer.spec
# Output: dist/BatchRenamer.exe
```

## Key Design Decisions

- **UI**: CustomTkinter (dark theme) + ttk.Treeview for file table
- **Drag-and-drop**: tkinterdnd2 (TkinterDnD.DnDWrapper mixin on CTk root)
- **Rule pipeline**: Each rule receives (stem, ext, index, total) and returns (stem, ext); rules compose sequentially
- **Conflict detection**: Case-insensitive key comparison, flagged before execute
- **Debounce**: Rule parameter changes trigger recompute after 100ms idle
