import libresvip
import libresvip.extension.base
from libresvip.extension.manager import plugin_manager
import music21
import music21.converter
import types
from types_linq import Enumerable
from typing import List, Dict, Tuple
import warnings

from music21_svs_formats.converter import LibresvipSubConverter


class ConverterException(music21.converter.ConverterException):
    pass


def libresvipSubConverter(
    format: str, plugin: type[libresvip.extension.base.SVSConverter]
) -> type[LibresvipSubConverter]:
    """
    Create a music21.converter.subConverters.SubConverter class for the given format and plugin.
    format: file extension without dot, such as mid
    plugin: a libresvip converter plugin object
    """
    can_input = not issubclass(plugin, libresvip.extension.base.WriteOnlyConverterMixin)
    can_output = not issubclass(plugin, libresvip.extension.base.ReadOnlyConverterMixin)
    return types.new_class(
        "libresvip_" + format,
        (LibresvipSubConverter,),
        {},
        lambda ns: ns.update(
            {
                "extension": format,
                "plugin_object": plugin,
                "registerFormats": (format,),
                "registerInputExtensions": (format,) * can_input,
                "registerOutputExtensions": (format,) * can_output,
            }
        ),
    )


subConverters: dict[str, type[LibresvipSubConverter]] = {}


def getSubConverterByFormat(format: str):
    if format in subConverters:
        return subConverters[format]
    if format not in plugin_manager.plugins["svs"]:
        raise ValueError(f"Format {format} is not supported by libresvip.")
    plugin = plugin_manager.plugins["svs"][format]
    converter = libresvipSubConverter(format, plugin)
    return converter


def registLibresvipPlugin(
    format: str, plugin: type[libresvip.extension.base.SVSConverter]
):
    subConverter = libresvipSubConverter(format, plugin)
    subConverters[format] = subConverter
    music21.converter.registerSubConverter(subConverter)


def registFormat(format: str):
    subConverter = getSubConverterByFormat(format)
    subConverters[format] = subConverter
    music21.converter.registerSubConverter(subConverter)


def registAllFormats():
    music21_builtin_formats = (
        Enumerable(music21.converter.Converter().subConvertersList("input"))
        .select_many(lambda x: x.registerInputExtensions)
        .to_list()
    )
    for x in Enumerable(plugin_manager.plugins["svs"].keys()).where(
        lambda x: x not in music21_builtin_formats
    ):
        registLibresvipPlugin(x, plugin_manager.plugins["svs"][x])


def unregistFormat(format: str):
    if format not in subConverters:
        raise ConverterException(f"Format {format} is not registered.")
    subConverter = subConverters[format]
    if subConverter not in music21.converter.Converter().subConvertersList():
        warnings.warn(
            f"Format {format} is not registered in music21.converter.Converter."
        )
    music21.converter.unregisterSubConverter(subConverter)
    del subConverters[format]


def unregistAllFormats():
    for format in list(subConverters.keys()):
        unregistFormat(format)
