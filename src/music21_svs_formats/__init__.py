import types
import music21
import music21.converter
import libresvip
from libresvip.extension.manager import plugin_manager
from py_linq import Enumerable
from typing import List, Dict, Tuple

from music21_svs_formats.converter import LibresvipSubConverter

def registLibresvipPlugin(format:str, plugin:libresvip.extension.base.SVSConverterBase):
    subConverter = types.new_class("libresvip_ustx", (LibresvipSubConverter,), {}, lambda ns: ns.update({
        "extension": format,
        "plugin_object": plugin,
        "registerFormats": (format,),
        "registerInputExtensions": (format,),
        "registerOutputExtensions": (format,)
    }))
    music21.converter.registerSubConverter(subConverter)

def registFormat(format:str):
    registLibresvipPlugin(format, plugin_manager.plugin_registry[format].plugin_object)

def registAllFormats():
    music21_builtin_formats = Enumerable(music21.converter.Converter().subConvertersList('input'))\
        .select_many(lambda x: x.registerInputExtensions)\
        .to_list()
    for x in Enumerable(plugin_manager.plugin_registry.keys())\
        .where(lambda x: x not in music21_builtin_formats):
        registLibresvipPlugin(x, plugin_manager.plugin_registry[x].plugin_object)
