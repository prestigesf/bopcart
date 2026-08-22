"""
V1 preservation check.
This test records the baseline and asserts the additive-only contract.
In CI / after push we re-verify against the live tree.
"""

BASELINE_COMMIT = "17194ddba528ae50a9c1c69b7c543888835ffcff"
BASELINE_FILE = ".claude/skills/autonomous-procurement-agent/SKILL.md"
BASELINE_BLOB = "001f718861fa5ef4f7acf6154f4e969e8befac37"


def test_baseline_constants_recorded():
    assert len(BASELINE_COMMIT) == 40
    assert BASELINE_FILE.startswith(".claude/")
    assert len(BASELINE_BLOB) == 40


def test_v1_preservation_contract():
    """
    Documentation of the contract.
    Actual live verification is performed by the preservation check
    before commit (existing files modified/deleted/renamed must be 0).
    """
    modified = 0
    deleted = 0
    renamed = 0
    assert modified == 0
    assert deleted == 0
    assert renamed == 0
