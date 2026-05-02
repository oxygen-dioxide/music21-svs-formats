# music21_svs_formats
Import and export Singing Voice Synthesis (SVS) project formats in [music21](https://github.com/cuthbertLab/music21) via [Libresvip](https://github.com/SoulMelody/LibreSVIP).

Music21 is designed for classical music theory, primarily centered around staff notation. With this library, users can easily convert SVS project files into sheet music readable by human singers and performers, or import MusicXML files (containing lyrics) downloaded from musescore.com into SVS software.

## Installation

```bash
git clone https://github.com/oxygen-dioxide/music21-svs-formats
cd music21-svs-formats
pip install -e .[hyphen]
```

## Features
- **Bi-directional conversion** between SVS software data and Music21 objects:
  - Notes, time signatures, and tempo.
  - Conversion between SVS melisma symbols (`-`) and musical slurs in staff notation.
- **Automatic completion** of metadata required by Music21 that is often absent in SVS projects:
  - Automatic key detection.
  - Automatic splitting note to tied notes when needed.
  - Automatic hyphenation of multi-syllabic lyrics (e.g., `listening` `+` `+` -> `lis`, `-ten`, `-ing`).

## Example
Convert an SVS project file to staff notation (requires [MuseScore](https://musescore.org/) installed):

```python
import music21
import music21_svs_formats

music21_svs_formats.registAllFormats()

infile = "path_to_your_file.ustx"
project = music21.converter.parseFile(infile, forceSource=True, hyphenLang="en_US")
project.show()
```