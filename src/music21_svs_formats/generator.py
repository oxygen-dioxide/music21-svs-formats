# convert music21.stream.Score to libresvip.model.base.Project
import music21
import music21.stream.base
import libresvip
import libresvip.model.base
from music21_svs_formats import util
import more_itertools
from types_linq import Enumerable

from typing import List, Tuple, Dict


def mTimeDistinct(stream: music21.stream.base.Stream):
    """
    Remove duplicate time signatures or tempos that have the same offset.
    """
    todelete: List[music21.base.Music21Object] = []
    for prev, curr in more_itertools.pairwise(stream):
        if prev.getOffsetBySite(stream) == curr.getOffsetBySite(stream):
            todelete.append(curr)
    for obj in todelete:
        stream.remove(obj)


def dumpNote(
    mNote: music21.note.Note, mPart: music21.stream.base.Stream
) -> libresvip.model.base.Note:
    """
    Convert music21.note.Note to libresvip.model.base.Note
    """
    lNote = libresvip.model.base.Note()
    lNote.start_pos = round(mNote.getOffsetBySite(mPart) * util.RESOLUTION)
    endTick = round(
        (mNote.getOffsetBySite(mPart) + mNote.duration.quarterLength) * util.RESOLUTION
    )
    lNote.length = endTick - lNote.start_pos
    lNote.key_number = mNote.pitch.midi
    if mNote.lyric is not None:
        lNote.lyric = mNote.lyric
    return lNote


def dumpTrack(mPart: music21.stream.base.Stream) -> libresvip.model.base.SingingTrack:
    """
    Convert music21.stream.base.Part to libresvip.model.base.SingingTrack
    """
    lTrack = libresvip.model.base.SingingTrack()
    if hasattr(mPart, "partName") and mPart.partName:
        lTrack.title = mPart.partName
    mPart = mPart.flatten().stripTies()
    for mGeneralNote in mPart.notesAndRests:
        if isinstance(mGeneralNote, music21.note.Note):
            lTrack.note_list.append(dumpNote(mGeneralNote, mPart))
        elif isinstance(mGeneralNote, music21.chord.Chord):
            for mNote in mGeneralNote.notes:
                lTrack.note_list.append(dumpNote(mNote, mPart))
    return lTrack


def dumpProject(mScore: music21.stream.base.Score) -> libresvip.model.base.Project:
    """
    Convert music21.stream.Score to libresvip.model.base.Project
    """
    lProject = libresvip.model.base.Project()
    if hasattr(mScore, "parts"):
        lProject.track_list = [dumpTrack(mPart) for mPart in mScore.parts]
    else:
        lProject.track_list = [dumpTrack(mScore)]
    flattenedScore = mScore.flatten()
    mTempos: music21.stream.Stream[music21.tempo.MetronomeMark] = music21.stream.Stream(
        flattenedScore.getElementsByClass(music21.tempo.MetronomeMark)
    )
    mTimeDistinct(mTempos)
    lProject.song_tempo_list = (
        Enumerable(mTempos)
        .select(
            lambda x: libresvip.model.base.SongTempo(
                Position=round(x.getOffsetBySite(flattenedScore) * util.RESOLUTION),
                BPM=x.number,
            )
        )
        .to_list()
    )
    if not lProject.song_tempo_list:
        lProject.song_tempo_list.append(
            libresvip.model.base.SongTempo(Position=0, BPM=120)
        )
    lProject.time_signature_list = (
        Enumerable(
            enumerate(
                flattenedScore.makeMeasures().getElementsByClass(music21.stream.Measure)
            )
        )
        .where(lambda x: x[1].timeSignature)
        .select(
            lambda x: libresvip.model.base.TimeSignature(
                bar_index=x[0],
                numerator=x[1].timeSignature.numerator,
                denominator=x[1].timeSignature.denominator,
            )
        )
        .to_list()
    )
    if not lProject.time_signature_list:
        lProject.time_signature_list.append(
            libresvip.model.base.TimeSignature(bar_index=0, numerator=4, denominator=4)
        )

    return lProject
