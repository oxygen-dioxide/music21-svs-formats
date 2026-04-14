import music21_svs_formats
import music21
from types_linq import Enumerable
import pytest


def test_regist():
    music21_svs_formats.registAllFormats()
    outputFormats = (
        Enumerable(music21.converter.Converter().subConvertersList("output"))
        .select_many(lambda x: x.registerOutputExtensions)
        .to_list()
    )
    inputFormats = (
        Enumerable(music21.converter.Converter().subConvertersList("input"))
        .select_many(lambda x: x.registerInputExtensions)
        .to_list()
    )
    assert "ustx" in outputFormats
    assert "ustx" in inputFormats
    assert "lrc" in outputFormats
    assert "lrc" not in inputFormats


def test_invalid_format():
    with pytest.raises(ValueError):
        music21_svs_formats.getSubConverterByFormat("invalid_format")
