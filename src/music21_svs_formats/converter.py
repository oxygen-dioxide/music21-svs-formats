import music21
import libresvip
from music21_svs_formats import parser
from music21_svs_formats import generator
from io import IOBase
import pathlib
from typing import List, Dict, Tuple, Optional, Iterable


class LibresvipSubConverter(music21.converter.subConverters.SubConverter):
    extension: str = ""  # file extension without dot, such as mid
    plugin_object: libresvip.extension.base.SVSConverter

    def parseFile(
        self,
        filePath: str | pathlib.Path,
        number: Optional[int] = None,
        hyphenDictPath: Optional[str | pathlib.Path] = None,
        hyphenLang: Optional[str] = None,
        **keywords,
    ) -> music21.stream.Score:
        filePath = pathlib.Path(filePath)
        lProject = self.plugin_object.load(filePath, {})
        if hyphenDictPath is not None:
            import pyphen

            hyphenDict = pyphen.Pyphen(filename=hyphenDictPath)
        elif hyphenLang is not None:
            import pyphen

            hyphenDict = pyphen.Pyphen(lang=hyphenLang)
        else:
            hyphenDict = None
        mScore = parser.parseProject(lProject, hyphenDict)
        self.stream = mScore
        return mScore

    def parseData(
        self, dataStr: str | bytes, number: Optional[int] = None
    ) -> music21.stream.Score:
        # get a temporary file path
        from music21 import environment

        e = environment.Environment()
        fp: pathlib.Path = e.getTempFile("." + self.extension)
        if isinstance(dataStr, str):
            fp.write_text(dataStr, encoding="utf-8")
        else:
            fp.write_bytes(dataStr)
        return self.parseFile(fp, number)

    def write(
        self,
        obj: music21.base.Music21Object,
        fmt: str | None,
        fp: str | pathlib.Path | IOBase | None = None,
        subformats: Iterable[str] = (),
        **keywords,
    ):
        lProject = generator.dumpProject(obj)
        if isinstance(fp, IOBase):
            from music21 import environment

            e = environment.Environment()
            file: pathlib.Path = e.getTempFile("." + self.extension)
            self.plugin_object.dump(file, lProject, {})
            fp.write(file.read_bytes())
            return fp
        if fp is None:
            fp = self.getTemporaryFile()
        self.plugin_object.dump(pathlib.Path(fp), lProject, {})
        return fp
