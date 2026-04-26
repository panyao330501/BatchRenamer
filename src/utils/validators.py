from core.rules import Rule, FullRenameRule, SerializeRule


def full_rename_needs_serialize(rules: list[Rule]) -> bool:
    """Return True when FullRenameRule is present but SerializeRule is absent.

    In that situation every file would receive the same stem, guaranteeing
    conflicts — the UI should warn the user and block execution.
    """
    has_full = any(isinstance(r, FullRenameRule) for r in rules)
    has_serial = any(isinstance(r, SerializeRule) for r in rules)
    return has_full and not has_serial
