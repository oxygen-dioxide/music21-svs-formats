import pathlib
import music21_svs_formats
import music21
import mido
import pretty_midi
import numpy
import pytest

from typing import Iterable


@pytest.fixture
def converter():
    return music21_svs_formats.getSubConverterByFormat("mid")()


@pytest.fixture
def env():
    return music21.environment.Environment()


@pytest.fixture
def midi_compare():
    def _compare(midi_path1: pathlib.Path, midi_path2: pathlib.Path):
        midi1 = pretty_midi.PrettyMIDI(str(midi_path1))
        midi2 = pretty_midi.PrettyMIDI(str(midi_path2))

        # Compare the number of instruments
        assert len(midi1.instruments) == len(midi2.instruments), "Number of instruments mismatch"

        # Compare each instrument
        for inst1, inst2 in zip(midi1.instruments, midi2.instruments):
            assert len(inst1.notes) == len(inst2.notes), "Number of notes mismatch"

            # Compare each note
            for note1, note2 in zip(inst1.notes, inst2.notes):
                assert note1.pitch == note2.pitch, "Pitch mismatch"
                assert note1.start == note2.start, "Start time mismatch"
                assert note1.end == note2.end, "End time mismatch"

    return _compare


@pytest.fixture
def prepare_midi():
    def _prepare(tones: Iterable[int]) -> mido.MidiFile:
        midi = mido.MidiFile()
        track = mido.MidiTrack()
        midi.tracks.append(track)

        for tone in tones:
            note_on = mido.Message('note_on', note=tone, velocity=64, time=0)
            note_off = mido.Message('note_off', note=tone, velocity=64, time=480)
            track.append(note_on)
            track.append(note_off)

        return midi

    return _prepare


@pytest.fixture
def convert_and_compare(converter, env, midi_compare):
    def _convert_and_compare(orig_file_path: pathlib.Path):
        dest_file_path = env.getTempFile(suffix=".mid")
        
        m_score = converter.parseFile(orig_file_path)
        m_score.write("midi", fp=dest_file_path)

        assert dest_file_path.exists(), f"Converted file {dest_file_path} does not exist."
        
        midi_compare(orig_file_path, dest_file_path)
        dest_file_path.unlink()

    return _convert_and_compare


def test_external_midi(converter, env, midi_compare):
    test_resources_path = pathlib.Path(__file__).parent / "resources"
    file_names = ["music21-test01.mid"]
    
    for file_name in file_names:
        orig_file_path = test_resources_path / file_name
        dest_file_path = env.getTempFile(suffix=".mid")

        m_score = converter.parseFile(orig_file_path)
        m_score.write("midi", fp=dest_file_path)

        assert dest_file_path.exists(), f"Converted file {dest_file_path} does not exist."
        
        midi_compare(orig_file_path, dest_file_path)
        dest_file_path.unlink()


def test_empty_midi(env, prepare_midi, convert_and_compare):
    orig_file_path = env.getTempFile(suffix=".mid")
    prepare_midi([]).save(orig_file_path)
    
    try:
        convert_and_compare(orig_file_path)
    finally:
        # Use finally to ensure the original temp file is cleaned up even if the test fails
        if orig_file_path.exists():
            orig_file_path.unlink()


@pytest.mark.parametrize("k", range(12))
def test_scales(k, env, prepare_midi, convert_and_compare):
    basic_scale = numpy.array([0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23], dtype=numpy.int32)
    
    orig_file_path = env.getTempFile(suffix=".mid")
    prepare_midi(basic_scale + k + 48).save(orig_file_path)
    
    try:
        convert_and_compare(orig_file_path)
    finally:
        if orig_file_path.exists():
            orig_file_path.unlink()
