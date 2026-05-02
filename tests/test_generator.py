import pathlib
import music21_svs_formats
import music21
import mido
import pretty_midi
import pytest

from typing import Iterable
from .utils import midi_compare, midi_converter, env


@pytest.fixture
def midi_generate_and_compare(midi_converter, env, midi_compare):
    def _midi_generate_and_compare(mScore: music21.stream.Score):
        expected_file_path = env.getTempFile(suffix=".mid")
        actual_file_path = env.getTempFile(suffix=".mid")

        mScore.write("midi", fp=expected_file_path)
        midi_converter.write(mScore, "midi", fp=actual_file_path)

        assert actual_file_path.exists(), (
            f"Converted file {actual_file_path} does not exist."
        )

        midi_compare(expected_file_path, actual_file_path)
        expected_file_path.unlink()
        actual_file_path.unlink()

    return _midi_generate_and_compare


@pytest.mark.parametrize(
    "name",
    [
        "bach/bwv65.2.xml",
    ],
)
def test_corpus_midi_generate(name, midi_generate_and_compare):
    mScore = music21.corpus.parse(name)
    midi_generate_and_compare(mScore)


def test_empty_midi_generate(midi_generate_and_compare):
    mScore = music21.stream.Score()
    midi_generate_and_compare(mScore)


def test_midi_generate_non_filename(midi_converter, env, midi_compare):
    mScore = music21.stream.Score()
    path = midi_converter.write(mScore, "midi")
    assert pathlib.Path(path).exists(), f"Generated MIDI file {path} does not exist."
    expected_file_path = env.getTempFile(suffix=".mid")
    mScore.write("midi", fp=expected_file_path)
    midi_compare(expected_file_path, path)
    expected_file_path.unlink()
    path.unlink()


def test_duplicate_tempo(midi_generate_and_compare):
    mScore = music21.stream.Stream(
        [
            music21.tempo.MetronomeMark(60),
            music21.tempo.MetronomeMark(70),
            music21.note.Note(60, quarterLength=4),
            music21.tempo.MetronomeMark(80),
            music21.tempo.MetronomeMark(90),
            music21.note.Note(62, quarterLength=4),
        ]
    )
    midi_generate_and_compare(mScore)


def test_non_stream_input(midi_generate_and_compare):
    mNote = music21.note.Note(60, quarterLength=4)
    midi_generate_and_compare(mNote)


# music21内置的midi解析器会将音符时值量化，无法保留原始midi文件中的时值信息。
