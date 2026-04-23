# Convert libresvip.model.base.Project to music21.stream.Score

import copy
import music21
import music21.stream.base
import music21.meter.base
import libresvip
import libresvip.model.base
from music21_svs_formats import util
import more_itertools
from types_linq import Enumerable

from typing import List, Tuple, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import pyphen


def parseTimeSignature(
    lTimeSignature: libresvip.model.base.TimeSignature,
) -> music21.meter.base.TimeSignature:
    mTimeSignature = music21.meter.base.TimeSignature()
    mTimeSignature.numerator = lTimeSignature.numerator
    mTimeSignature.denominator = lTimeSignature.denominator
    return mTimeSignature


def parseTempo(lTempo: libresvip.model.base.SongTempo) -> music21.tempo.MetronomeMark:
    mTempo = music21.tempo.MetronomeMark()
    mTempo.number = lTempo.bpm
    return mTempo


def hyphen(lTrack: libresvip.model.base.SingingTrack, hyphenDict: "pyphen.Pyphen"):
    """
    `listening` `+` -> `lis-` `-ten-` `-ing`
    """
    wordStart: libresvip.model.base.Note | None = None
    placeHolderNotes: List[libresvip.model.base.Note] = []

    for lNote in lTrack.note_list:
        if lNote.lyric == "-":  # slur note, remain unchanged
            continue
        if lNote.lyric == "+":
            placeHolderNotes.append(lNote)
        else:
            if wordStart and len(placeHolderNotes) > 0:
                syllables = hyphenDict.inserted(wordStart.lyric).split("-")
                if len(syllables) > len(placeHolderNotes) + 1:
                    syllables[len(placeHolderNotes)] = "".join(
                        syllables[len(placeHolderNotes) :]
                    )
                syllables = "- -".join(syllables).split(" ")
                wordStart.lyric = syllables[0]
                for note, syllable in zip([wordStart] + placeHolderNotes, syllables):
                    note.lyric = syllable
            wordStart = lNote
            placeHolderNotes.clear()


def parseTrack(
    lTrack: libresvip.model.base.SingingTrack, hyphenDict: "pyphen.Pyphen | None" = None
) -> music21.stream.base.Part:
    if hyphenDict is not None:
        hyphen(lTrack, hyphenDict)
    mPart = music21.stream.base.Part()
    slurs: List[music21.note.Note] = []
    prevmNote: Optional[music21.note.Note] = None
    for lNote in lTrack.note_list:
        mNote = music21.note.Note(
            lNote.key_number,
            duration=music21.duration.Duration(lNote.length / util.RESOLUTION),
        )
        if lNote.lyric == "-":  # slur note
            if len(slurs) != 0:
                slurs.append(mNote)
            else:
                if prevmNote != None:
                    slurs.append(prevmNote)
                    slurs.append(mNote)
        else:
            if len(slurs) > 0:
                mPart.append(music21.spanner.Slur(slurs))
                slurs.clear()
            mNote.lyric = lNote.lyric
            prevmNote = mNote
        mPart.insert(lNote.start_pos / util.RESOLUTION, mNote)

    if len(slurs) > 0:
        mPart.append(music21.spanner.Slur(slurs))
        slurs.clear()
    mPart.partName = lTrack.title
    return mPart


def scoreWiseInsert(
    mScore: music21.stream.base.Score,
    quarterPosition,
    object: music21.base.Music21Object,
):
    """
    Insert an object to all parts of the score at the given quarterPosition
    """
    for mPart in mScore.parts:
        mPart.insert(quarterPosition, object)


def applyKey(mScore: music21.stream.base.Score, key: music21.key.Key):
    """
    Apply the key signature to all parts of the score
    """
    numberToPitch = Enumerable(key.getPitches()).to_dict(
        lambda x: x.midi % 12, lambda x: x
    )
    scoreWiseInsert(mScore, 0, key)
    for mNote in mScore.recurse().notes:
        midi = mNote.pitch.midi
        if mNote.pitch.midi % 12 in numberToPitch:
            destPitch = copy.deepcopy(numberToPitch[mNote.pitch.midi % 12])
            destPitch.octave = destPitch.octave + (midi - destPitch.midi) // 12
            mNote.pitch = destPitch
    mScore.makeNotation(inPlace=True)


def parseProject(
    lProject: libresvip.model.base.Project, hyphenDict: "pyphen.Pyphen | None" = None
) -> music21.stream.Score:
    lProject = copy.deepcopy(lProject)
    mScore = music21.stream.base.Score()
    # parse tracks
    for lTrack in lProject.track_list:
        if isinstance(lTrack, libresvip.model.base.SingingTrack):
            mScore.append(parseTrack(lTrack, hyphenDict))
    # parse time signatures
    quarterPosition: float = 0
    lTimeSignatures = lProject.time_signature_list
    if len(lTimeSignatures) == 0 or lTimeSignatures[0].bar_index > 0:
        lTimeSignatures = [libresvip.model.base.TimeSignature()] + lTimeSignatures
    for currTs, nextTs in more_itertools.pairwise(lTimeSignatures):
        if currTs.bar_index < nextTs.bar_index:
            scoreWiseInsert(mScore, quarterPosition, parseTimeSignature(currTs))
            quarterPosition += (
                (nextTs.bar_index - currTs.bar_index)
                * 4
                * currTs.numerator
                / currTs.denominator
            )
    scoreWiseInsert(mScore, quarterPosition, parseTimeSignature(lTimeSignatures[-1]))
    # parse tempo
    lTempos = lProject.song_tempo_list
    if len(lTempos) == 0 or lTempos[0].position > 0:
        lTempos = [libresvip.model.base.SongTempo()] + lTempos
    for currTempo, nextTempo in more_itertools.pairwise(lTempos):
        if currTempo.position < nextTempo.position:
            scoreWiseInsert(
                mScore,
                currTempo.position / util.RESOLUTION,
                music21.tempo.MetronomeMark(number=currTempo.bpm),
            )
    scoreWiseInsert(
        mScore,
        lTempos[-1].position / util.RESOLUTION,
        music21.tempo.MetronomeMark(number=lTempos[-1].bpm),
    )

    # Detect key
    # Singing synthesizer formats usually don't care about key, so we have to detect it.
    try:
        key = mScore.analyze("key")
        applyKey(mScore, key)
    except music21.analysis.discrete.DiscreteAnalysisException:
        pass

    for mPart in mScore.parts:
        mPart.makeMeasures(inPlace=True)
    if len(mScore) > 0:
        mScore.makeTies(inPlace=True)
    mScore.makeRests(inPlace=True, fillGaps=True, timeRangeFromBarDuration=True)
    return mScore
