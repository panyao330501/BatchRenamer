from __future__ import annotations
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass


class Rule(ABC):
    @abstractmethod
    def apply(self, stem: str, ext: str, index: int, total: int) -> tuple[str, str]:
        pass

    @property
    @abstractmethod
    def rule_type(self) -> str:
        pass


@dataclass
class ChangeExtRule(Rule):
    """Replace, add (if missing), or remove the file extension."""
    mode: str = "replace"   # "replace" | "add" | "remove"
    new_ext: str = ""

    @property
    def rule_type(self) -> str:
        return "extension"

    def apply(self, stem: str, ext: str, index: int, total: int) -> tuple[str, str]:
        if self.mode == "replace":
            ne = self.new_ext.strip()
            if ne and not ne.startswith("."):
                ne = "." + ne
            return stem, ne
        if self.mode == "add":
            if not ext:
                ne = self.new_ext.strip()
                if ne and not ne.startswith("."):
                    ne = "." + ne
                return stem, ne
            return stem, ext
        if self.mode == "remove":
            return stem, ""
        return stem, ext


@dataclass
class SerializeRule(Rule):
    """Insert a sequential number into the filename.

    The pattern string acts as a placeholder; the first occurrence is replaced
    by the padded number. If the pattern is not found in stem, the number is
    appended to stem. padding=0 means auto-calculate from total file count.
    """
    pattern: str = "#"
    start: int = 1
    padding: int = 0    # 0 = auto

    @property
    def rule_type(self) -> str:
        return "serialize"

    def apply(self, stem: str, ext: str, index: int, total: int) -> tuple[str, str]:
        pad = self.padding if self.padding > 0 else len(str(total + self.start - 1))
        num_str = str(index + self.start).zfill(pad)
        if self.pattern and self.pattern in stem:
            new_stem = stem.replace(self.pattern, num_str, 1)
        else:
            new_stem = stem + num_str
        return new_stem, ext


@dataclass
class SliceKeepRule(Rule):
    """Keep only characters n..m of the stem (1-indexed, inclusive). m=-1 means end."""
    n: int = 1
    m: int = -1

    @property
    def rule_type(self) -> str:
        return "slice_keep"

    def apply(self, stem: str, ext: str, index: int, total: int) -> tuple[str, str]:
        start = max(0, self.n - 1)
        if self.m == -1:
            return stem[start:], ext
        end = max(start, self.m)
        return stem[start:end], ext


@dataclass
class SliceDeleteRule(Rule):
    """Delete characters n..m of the stem (1-indexed, inclusive).
    Out-of-bounds indices are clamped — never raises.
    """
    n: int = 1
    m: int = 1

    @property
    def rule_type(self) -> str:
        return "slice_delete"

    def apply(self, stem: str, ext: str, index: int, total: int) -> tuple[str, str]:
        start = max(0, self.n - 1)
        end = min(max(start, self.m), len(stem))
        return stem[:start] + stem[end:], ext


@dataclass
class InsertRule(Rule):
    """Insert text at a given position in stem.

    pos=0  → prepend (before all characters)
    pos>0  → insert after the pos-th character (1-indexed)
    pos<0  → append (after all characters)
    """
    text: str = ""
    pos: int = 0

    @property
    def rule_type(self) -> str:
        return "insert"

    def apply(self, stem: str, ext: str, index: int, total: int) -> tuple[str, str]:
        if not self.text:
            return stem, ext
        if self.pos < 0:
            return stem + self.text, ext
        insert_at = min(self.pos, len(stem))
        return stem[:insert_at] + self.text + stem[insert_at:], ext


@dataclass
class FullRenameRule(Rule):
    """Replace the entire stem with a fixed name.
    Must be paired with SerializeRule to avoid conflicts when multiple files exist.
    """
    name: str = "file"

    @property
    def rule_type(self) -> str:
        return "full_rename"

    def apply(self, stem: str, ext: str, index: int, total: int) -> tuple[str, str]:
        return self.name, ext


@dataclass
class ClearChineseRule(Rule):
    """Remove all CJK Unified Ideograph characters from stem."""

    @property
    def rule_type(self) -> str:
        return "clear_chinese"

    def apply(self, stem: str, ext: str, index: int, total: int) -> tuple[str, str]:
        cleaned = re.sub(r"[一-鿿㐀-䶿豈-﫿　-〿]+", "", stem)
        return cleaned, ext


@dataclass
class DeleteStringRule(Rule):
    """Remove every occurrence of a specific string from stem."""
    target: str = ""

    @property
    def rule_type(self) -> str:
        return "delete_string"

    def apply(self, stem: str, ext: str, index: int, total: int) -> tuple[str, str]:
        if not self.target:
            return stem, ext
        return stem.replace(self.target, ""), ext
