import music21
import libresvip
from music21_svs_formats import parser
from music21_svs_formats import generator
import pathlib
from typing import List, Dict, Tuple, Optional
from typing import get_type_hints

class LibresvipSubConverter(music21.converter.subConverters.SubConverter):
    extension:str = "" # file extension without dot, such as mid
    plugin_object:Optional[libresvip.extension.base.SVSConverterBase] = None

    def parseFile(self, filePath: str | pathlib.Path, number:int) -> music21.stream.Score:
        filePath = pathlib.Path(filePath)
        input_option = get_type_hints(self.plugin_object.load).get("options")()
        lProject = self.plugin_object.load(filePath, input_option)
        mScore = parser.parseProject(lProject)
        self.stream = mScore
        return mScore
    
    def parseData(self, dataStr: str | bytes, number:int) -> music21.stream.Score:
        #get a temporary file path
        from music21 import environment
        e = environment.Environment()
        fp:pathlib.Path = e.getTempFile("." + self.extension)
        if(isinstance(dataStr, str)):
            fp.write_text(dataStr, encoding="utf-8")
        else:
            fp.write_bytes(dataStr)
        return self.parseFile(fp, number)
    
    def write(self, obj, fmt, fp=None, subformats=(), **keywords):
        lProject = generator.dumpProject(obj)
        if fp is None:
            fp = self.getTemporaryFile()
        output_option = get_type_hints(self.plugin_object.dump).get("options")()
        self.plugin_object.dump(pathlib.Path(fp), lProject, output_option)
        return fp