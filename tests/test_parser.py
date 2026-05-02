import pathlib
import music21_svs_formats
import music21
import mido
import pretty_midi
import numpy
import pytest

from typing import Iterable
from .utils import midi_compare, midi_converter, env, ustx_converter

test_resources_path = pathlib.Path(__file__).parent / "resources"


@pytest.fixture
def prepare_midi():
    def _prepare(tones: Iterable[int]) -> mido.MidiFile:
        midi = mido.MidiFile()
        track = mido.MidiTrack()
        midi.tracks.append(track)

        for tone in tones:
            note_on = mido.Message("note_on", note=tone, velocity=64, time=0)
            note_off = mido.Message("note_off", note=tone, velocity=64, time=480)
            track.append(note_on)
            track.append(note_off)

        return midi

    return _prepare


@pytest.fixture
def midi_parse_and_compare(midi_converter, env, midi_compare):
    def _midi_parse_and_compare(orig_file_path: pathlib.Path):
        dest_file_path = env.getTempFile(suffix=".mid")

        m_score = midi_converter.parseFile(orig_file_path)
        m_score.write("midi", fp=dest_file_path)

        assert dest_file_path.exists(), (
            f"Converted file {dest_file_path} does not exist."
        )

        midi_compare(orig_file_path, dest_file_path)
        dest_file_path.unlink()
        return m_score

    return _midi_parse_and_compare


@pytest.mark.parametrize(
    "file_name",
    [
        "music21-test01.mid",
    ],
)
def test_external_midi_parse(file_name, midi_parse_and_compare):
    orig_file_path = test_resources_path / file_name

    midi_parse_and_compare(orig_file_path)


def test_empty_midi_parse(env, prepare_midi, midi_parse_and_compare):
    orig_file_path = env.getTempFile(suffix=".mid")
    prepare_midi([]).save(orig_file_path)

    try:
        midi_parse_and_compare(orig_file_path)
    finally:
        # Use finally to ensure the original temp file is cleaned up even if the test fails
        if orig_file_path.exists():
            orig_file_path.unlink()


@pytest.mark.parametrize("k", range(12))
def test_scales(k, env, prepare_midi, midi_parse_and_compare):
    basic_scale = numpy.array(
        [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23], dtype=numpy.int32
    )

    orig_file_path = env.getTempFile(suffix=".mid")
    prepare_midi(basic_scale + k + 48).save(orig_file_path)

    try:
        m_score = midi_parse_and_compare(orig_file_path)
        kss = m_score.flatten().getElementsByClass(music21.key.KeySignature)
        assert len(kss) == 1, "There should be exactly one key signature in the score."
        assert kss[0].asKey().getRelativeMajor().getTonic().midi % 12 == k, (
            "The key signature should correspond to the correct tonic."
        )
    finally:
        if orig_file_path.exists():
            orig_file_path.unlink()


def test_multisyllable():
    ustx_path = test_resources_path / "test-multisyllable.ustx"
    c = ustx_converter()
    m_score = c.parseFile(ustx_path, hyphenLang="en_US")
    assert len(m_score.parts) == 1, "There should be exactly one part in the score."
    part = m_score.parts[0]
    notes = list(part.flatten().notes)
    assert len(notes) == 3, "There should be exactly three notes in the part."

    expected_lyrics = ["lis", "ten", "ing"]
    expected_lyric_syllabics = ["begin", "middle", "end"]

    for note, expected_lyric, expected_syllabic in zip(
        notes, expected_lyrics, expected_lyric_syllabics
    ):
        assert note.lyric == expected_lyric, (
            f"Expected lyric '{expected_lyric}' but got '{note.lyric}'"
        )
        assert note.lyrics[0].syllabic == expected_syllabic, (
            f"Expected syllabic '{expected_syllabic}' but got '{note.lyrics[0].syllabic}'"
        )
