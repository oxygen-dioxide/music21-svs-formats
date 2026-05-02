import pytest
import pretty_midi
import pathlib
import music21
import music21_svs_formats


@pytest.fixture
def midi_converter():
    return music21_svs_formats.getSubConverterByFormat("mid")()


def ustx_converter():
    return music21_svs_formats.getSubConverterByFormat("ustx")()


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
            f"Number of instruments mismatch: {len(midi1.instruments)} vs {len(midi2.instruments)}"
        )

        # Compare each instrument
        for inst1, inst2 in zip(midi1.instruments, midi2.instruments):
            assert len(inst1.notes) == len(inst2.notes), (
                f"Number of notes mismatch: {len(inst1.notes)} vs {len(inst2.notes)}"
            )

            # Compare each note
            for note1, note2 in zip(inst1.notes, inst2.notes):
                assert note1.pitch == note2.pitch, (
                    f"Pitch mismatch: {note1.pitch} vs {note2.pitch}"
                )
                assert note1.start == note2.start, (
                    f"Start time mismatch: {note1.start} vs {note2.start}"
                )
                assert note1.end == note2.end, (
                    f"End time mismatch: {note1.end} vs {note2.end}"
                )

    return _compare
