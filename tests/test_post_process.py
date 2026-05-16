import copy
import music21
import music21.stream.base
import pytest

from music21_svs_formats.post_process import (
    stripEmptyBars,
    lstripEmptyBars,
    rstripEmptyBars,
)


def _makeMeasure(hasNote: bool = False) -> music21.stream.Measure:
    m = music21.stream.Measure()
    if hasNote:
        m.append(music21.note.Note("C4", quarterLength=4))
    else:
        m.append(music21.note.Rest(quarterLength=4))
    return m


def _makeScore(partPatterns: list[list[bool]]) -> music21.stream.base.Score:
    score = music21.stream.base.Score()
    for i, pattern in enumerate(partPatterns):
        part = music21.stream.base.Part()
        part.partName = f"Part {i}"
        for hasNote in pattern:
            part.append(_makeMeasure(hasNote))
        score.append(part)
    return score


def _countMeasures(score: music21.stream.base.Score) -> list[int]:
    return [
        len(list(p.getElementsByClass(music21.stream.Measure)))
        for p in score.parts
    ]


def _countNotes(score: music21.stream.base.Score) -> list[int]:
    return [
        len(list(p.flatten().getElementsByClass(music21.note.Note)))
        for p in score.parts
    ]


class TestLstripEmptyBars:
    def test_strips_leading_empty(self):
        score = _makeScore([[False, False, True, True]])
        result = lstripEmptyBars(score, inPlace=False)
        assert _countMeasures(result) == [2]
        assert _countNotes(result) == [2]

    def test_no_leading_empty(self):
        score = _makeScore([[True, False, True]])
        result = lstripEmptyBars(score, inPlace=False)
        assert _countMeasures(result) == [3]
        assert _countNotes(result) == [2]

    def test_all_empty_returns_same(self):
        score = _makeScore([[False, False]])
        result = lstripEmptyBars(score, inPlace=False)
        assert _countMeasures(result) == [2]

    def test_single_part_no_measures(self):
        score = music21.stream.base.Score()
        score.append(music21.stream.base.Part())
        result = lstripEmptyBars(score, inPlace=False)
        assert _countMeasures(result) == [0]

    def test_empty_score(self):
        score = music21.stream.base.Score()
        result = lstripEmptyBars(score, inPlace=False)
        assert len(result.parts) == 0

    def test_inplace_true_modifies_original(self):
        score = _makeScore([[False, True]])
        original_id = id(score)
        result = lstripEmptyBars(score, inPlace=True)
        assert id(result) == original_id
        assert _countMeasures(result) == [1]

    def test_inplace_false_returns_copy(self):
        score = _makeScore([[False, True]])
        original_id = id(score)
        result = lstripEmptyBars(score, inPlace=False)
        assert id(result) != original_id
        assert _countMeasures(score) == [2]
        assert _countMeasures(result) == [1]

    def test_multiple_parts_cross_part_empty_measure(self):
        score = _makeScore([
            [False, False, True, False],
            [False, True, False, False],
        ])
        result = lstripEmptyBars(score, inPlace=False)
        assert _countMeasures(result) == [3, 3]


class TestRstripEmptyBars:
    def test_strips_trailing_empty(self):
        score = _makeScore([[True, True, False, False]])
        result = rstripEmptyBars(score, inPlace=False)
        assert _countMeasures(result) == [2]
        assert _countNotes(result) == [2]

    def test_no_trailing_empty(self):
        score = _makeScore([[True, False, True]])
        result = rstripEmptyBars(score, inPlace=False)
        assert _countMeasures(result) == [3]
        assert _countNotes(result) == [2]

    def test_all_empty_returns_same(self):
        score = _makeScore([[False, False]])
        result = rstripEmptyBars(score, inPlace=False)
        assert _countMeasures(result) == [2]

    def test_inplace_true_modifies_original(self):
        score = _makeScore([[True, False]])
        original_id = id(score)
        result = rstripEmptyBars(score, inPlace=True)
        assert id(result) == original_id
        assert _countMeasures(result) == [1]

    def test_inplace_false_returns_copy(self):
        score = _makeScore([[True, False]])
        original_id = id(score)
        result = rstripEmptyBars(score, inPlace=False)
        assert id(result) != original_id
        assert _countMeasures(score) == [2]
        assert _countMeasures(result) == [1]

    def test_multiple_parts(self):
        score = _makeScore([
            [False, True, False, False],
            [True, False, False, False],
        ])
        result = rstripEmptyBars(score, inPlace=False)
        assert _countMeasures(result) == [2, 2]


class TestStripEmptyBars:
    def test_strips_both_ends(self):
        score = _makeScore([[False, True, True, False]])
        result = stripEmptyBars(score, inPlace=False)
        assert _countMeasures(result) == [2]
        assert _countNotes(result) == [2]

    def test_only_leading_empty(self):
        score = _makeScore([[False, True, True]])
        result = stripEmptyBars(score, inPlace=False)
        assert _countMeasures(result) == [2]
        assert _countNotes(result) == [2]

    def test_only_trailing_empty(self):
        score = _makeScore([[True, True, False]])
        result = stripEmptyBars(score, inPlace=False)
        assert _countMeasures(result) == [2]
        assert _countNotes(result) == [2]

    def test_no_empty_measures(self):
        score = _makeScore([[True, True, True]])
        result = stripEmptyBars(score, inPlace=False)
        assert _countMeasures(result) == [3]
        assert _countNotes(result) == [3]

    def test_inplace_false_preserves_original(self):
        score = _makeScore([[False, True, False]])
        original_count = _countMeasures(score)
        _ = stripEmptyBars(score, inPlace=False)
        assert _countMeasures(score) == original_count

    def test_inplace_true_modifies_original(self):
        score = _makeScore([[False, True, False]])
        original_id = id(score)
        result = stripEmptyBars(score, inPlace=True)
        assert id(result) == original_id

    def test_multiple_parts(self):
        score = _makeScore([
            [False, False, True, False],
            [False, True, True, False],
        ])
        result = stripEmptyBars(score, inPlace=False)
        assert _countMeasures(result) == [2, 2]
