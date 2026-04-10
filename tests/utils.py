import pytest
import pretty_midi
import pathlib
import music21
import music21_svs_formats


@pytest.fixture
def midi_converter():
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
        assert len(midi1.instruments) == len(midi2.instruments), (
            "Number of instruments mismatch"
        )

        # Compare each instrument
        for inst1, inst2 in zip(midi1.instruments, midi2.instruments):
            assert len(inst1.notes) == len(inst2.notes), "Number of notes mismatch"

            # Compare each note
            for note1, note2 in zip(inst1.notes, inst2.notes):
                assert note1.pitch == note2.pitch, "Pitch mismatch"
                assert note1.start == note2.start, "Start time mismatch"
                assert note1.end == note2.end, "End time mismatch"

    return _compare
