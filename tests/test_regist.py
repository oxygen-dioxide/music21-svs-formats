import music21_svs_formats
import music21
from types_linq import Enumerable
import pytest


@pytest.fixture
def get_music21_output_formats():
    def _get_music21_output_formats():
        return (
            Enumerable(music21.converter.Converter().subConvertersList("output"))
            .select_many(lambda x: x.registerOutputExtensions)
            .to_list()
        )

    return _get_music21_output_formats


@pytest.fixture
def get_music21_input_formats():
    def _get_music21_input_formats():
        return (
            Enumerable(music21.converter.Converter().subConvertersList("input"))
            .select_many(lambda x: x.registerInputExtensions)
            .to_list()
        )

    return _get_music21_input_formats


def test_regist(get_music21_output_formats, get_music21_input_formats):
    try:
        music21_svs_formats.registAllFormats()
        outputFormats = get_music21_output_formats()
        inputFormats = get_music21_input_formats()
        assert "ustx" in outputFormats
        assert "ustx" in inputFormats
        assert "lrc" in outputFormats
        assert "lrc" not in inputFormats

        music21_svs_formats.unregistFormat("ustx")
        outputFormats = get_music21_output_formats()
        inputFormats = get_music21_input_formats()
        assert "ustx" not in outputFormats
        assert "ustx" not in inputFormats
        assert "lrc" in outputFormats
        assert "lrc" not in inputFormats

        music21_svs_formats.unregistAllFormats()
        outputFormats = get_music21_output_formats()
        inputFormats = get_music21_input_formats()
        assert "ustx" not in outputFormats
        assert "ustx" not in inputFormats
        assert "lrc" not in outputFormats
        assert "lrc" not in inputFormats
    finally:
        music21.converter.resetSubConverters()


def test_invalid_format():
    with pytest.raises(ValueError):
        music21_svs_formats.getSubConverterByFormat("invalid_format")
