# BatchRenamer — Milestones

## Completed

### v0.1 — Project Scaffold
- Project structure, dependencies, CLAUDE.md
- Conda environment: `rename` at `C:\Users\A\miniconda3\envs\rename`

### v0.2 — Core Rule Engine
- 8 rule types implemented: Extension, Serialize, SliceKeep, SliceDelete, Insert, FullRename, ClearChinese, DeleteString
- Rules compose as a pipeline (stem, ext, index, total) → (stem, ext)
- Edge case handling: out-of-bounds slices, empty stems, locked files

### v0.3 — Full UI Application
- Modern dark-themed window (CustomTkinter)
- File list panel: Original / New Name / Status columns (ttk.Treeview)
- Rule panel: scrollable cards, add/remove per rule type
- Top toolbar: Add Files, Add Folder, wildcard path scan
- Bottom toolbar: Execute Rename, Clear List, status bar
- Real-time preview with 100ms debounce
- Drag-and-drop file/folder support (tkinterdnd2)
- Conflict detection → red highlight + Execute disabled
- FullRename-without-Serialize warning inline on card

### v1.0 — PyInstaller Packaging
- Single-file `.exe`, no console window
- All assets bundled (customtkinter themes, tkinterdnd2 DLLs)

---

## TODO / Future

- [ ] Undo / Redo (Ctrl+Z / Ctrl+Y) for renames
- [ ] Rule preset save/load (JSON profiles)
- [ ] Column sorting in file table
- [ ] Rule reordering via drag-and-drop in rule panel
- [ ] Recursive folder scanning option
- [ ] Filter files by extension in the file list
- [ ] Settings panel (default padding, date format tokens)
- [ ] Localization (Chinese UI)
