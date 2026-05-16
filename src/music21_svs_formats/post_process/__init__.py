"""
Post-processing functions for music21 streams.

Provides functions to strip empty bars (measures containing no notes or chords)
from the beginning and/or end of a music21 Score. This is useful for removing
intro/outro silence common in singing voice synthesis projects.
"""

import copy
import music21
import music21.stream.base
from typing import Optional


def _measureHasNotes(mMeasure: music21.stream.Measure) -> bool:
    for el in mMeasure.recurse():
        if isinstance(el, (music21.note.Note, music21.chord.Chord)):
            return True
    return False


def lstripEmptyBars(
    mScore: music21.stream.base.Score,
    inPlace: bool = False,
) -> music21.stream.base.Score:
    """
    Remove leading empty measures from a Score.

    A measure is considered empty if it contains no Note or Chord objects.

    Args:
        mScore: The music21 Score to process.
        inPlace: If True, modify the Score in place. If False, return a copy.

    Returns:
        The processed music21 Score.
    """
    if not inPlace:
        mScore = copy.deepcopy(mScore)

    if not mScore.parts:
        return mScore

    firstNonEmptyIdx: Optional[int] = None
    for mPart in mScore.parts:
        measures = list(mPart.getElementsByClass(music21.stream.Measure))
        for i, mMeasure in enumerate(measures):
            if _measureHasNotes(mMeasure):
                if firstNonEmptyIdx is None or i < firstNonEmptyIdx:
                    firstNonEmptyIdx = i
                break

    if firstNonEmptyIdx is None or firstNonEmptyIdx == 0:
        return mScore

    for mPart in mScore.parts:
        measures = list(mPart.getElementsByClass(music21.stream.Measure))
        for i in range(firstNonEmptyIdx):
            if i < len(measures):
                mPart.remove(measures[i])

    return mScore


def rstripEmptyBars(
    mScore: music21.stream.base.Score,
    inPlace: bool = False,
) -> music21.stream.base.Score:
    """
    Remove trailing empty measures from a Score.

    A measure is considered empty if it contains no Note or Chord objects.

    Args:
        mScore: The music21 Score to process.
        inPlace: If True, modify the Score in place. If False, return a copy.

    Returns:
        The processed music21 Score.
    """
    if not inPlace:
        mScore = copy.deepcopy(mScore)

    if not mScore.parts:
        return mScore

    lastNonEmptyIdx: Optional[int] = None
    for mPart in mScore.parts:
        measures = list(mPart.getElementsByClass(music21.stream.Measure))
        for i in range(len(measures) - 1, -1, -1):
            if _measureHasNotes(measures[i]):
                if lastNonEmptyIdx is None or i > lastNonEmptyIdx:
                    lastNonEmptyIdx = i
                break

    if lastNonEmptyIdx is None:
        return mScore

    for mPart in mScore.parts:
        measures = list(mPart.getElementsByClass(music21.stream.Measure))
        for i in range(len(measures) - 1, lastNonEmptyIdx, -1):
            if i < len(measures):
                mPart.remove(measures[i])

    return mScore


def stripEmptyBars(
    mScore: music21.stream.base.Score,
    inPlace: bool = False,
) -> music21.stream.base.Score:
    """
    Remove both leading and trailing empty measures from a Score.

    Equivalent to calling lstripEmptyBars then rstripEmptyBars.

    Args:
        mScore: The music21 Score to process.
        inPlace: If True, modify the Score in place. If False, return a copy.

    Returns:
        The processed music21 Score.
    """
    if not inPlace:
        mScore = copy.deepcopy(mScore)

    mScore = lstripEmptyBars(mScore, inPlace=True)
    mScore = rstripEmptyBars(mScore, inPlace=True)

    return mScore
