# convert music21.stream.Score to libresvip.model.base.Project
import music21
import music21.stream.base
import libresvip
import libresvip.model.base
from music21_svs_formats import util
import more_itertools
from py_linq import Enumerable

from typing import List, Tuple, Dict

def mTimeDistinct(stream:music21.stream.base.Stream):
    todelete:List[music21.base.Music21Object] = []
    for (prev, curr) in more_itertools.pairwise(stream):
        if(prev.getOffsetBySite(stream) == curr.getOffsetBySite(stream)):
            todelete.append(prev)
    for obj in todelete:
        stream.remove(obj)

def dumpTrack(mPart:music21.stream.base.Part) -> libresvip.model.base.SingingTrack:
    lTrack = libresvip.model.base.SingingTrack()
    lTrack.title = mPart.partName
    mPart = mPart.flatten()
    for mNote in mPart.notesAndRests:
        lNote = libresvip.model.base.Note()
        lNote.start_pos = round(mNote.getOffsetBySite(mPart) * util.RESOLUTION)
        endTick = round((mNote.getOffsetBySite(mPart) + mNote.duration.quarterLength) * util.RESOLUTION)
        lNote.length = endTick - lNote.start_pos
        lNote.key_number = mNote.pitch.midi
        if(mNote.lyric is not None):
            lNote.lyric = mNote.lyric
        lTrack.note_list.append(lNote)
    return lTrack

def dumpProject(mScore:music21.stream.base.Score) -> libresvip.model.base.Project:
    lProject = libresvip.model.base.Project()
    lProject.track_list = [dumpTrack(mPart) for mPart in mScore.parts]
    mTempos = mScore.getElementsByClass(music21.tempo.MetronomeMark)
    mTimeDistinct(mTempos)
    lProject.song_tempo_list = Enumerable(mTempos)\
        .select(lambda x: libresvip.model.base.SongTempo(
            Position=round(x.getOffsetBySite(mScore) * util.RESOLUTION), 
            bpm=x.number))\
        .to_list()
    return lProject