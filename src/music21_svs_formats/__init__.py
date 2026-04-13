import types
import music21
import music21.converter
import libresvip
import libresvip.extension.base
from libresvip.extension.manager import plugin_manager
from types_linq import Enumerable
from typing import List, Dict, Tuple

from music21_svs_formats.converter import LibresvipSubConverter


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


def getSubConverterByFormat(format: str):
    if format not in plugin_manager.plugins["svs"]:
        raise ValueError(f"Format {format} is not supported by libresvip.")
    plugin = plugin_manager.plugins["svs"][format]
    return libresvipSubConverter(format, plugin)


def registLibresvipPlugin(
    format: str, plugin: type[libresvip.extension.base.SVSConverter]
):
    subConverter = libresvipSubConverter(format, plugin)
    music21.converter.registerSubConverter(subConverter)


def registFormat(format: str):
    subConverter = getSubConverterByFormat(format)
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
