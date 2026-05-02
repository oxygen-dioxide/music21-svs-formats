# music21_svs_formats
通过 [Libresvip](https://github.com/SoulMelody/LibreSVIP) 在 [music21](https://github.com/cuthbertLab/music21) 中导入、导出歌声合成工程文件格式

Music21面向以五线谱为主要显示形式的经典乐理学。使用这个库，用户可以方便地将歌声合成工程文件转换为方便人类歌手和演奏者阅读的五线谱，或将从 musescore.com 中下载的，包含歌词的 musicxml 文件导入歌声合成软件。

## 安装

```bash
pip install music21_svs_formats
```

如需处理多音节语言：
```bash
pip install music21_svs_formats[hyphen]
```

## 功能
- 将歌声合成软件中的信息与 Music21 中的对应信息互转
  - 音符、拍号、速度转换
  - 歌声合成软件中的一字多音`-`与乐谱中的圆滑线互转
- 补全歌声合成工程中不关心，但是 Music21 关心的信息
  - 自动检测调性
  - 自动拆分延音线
  - 自动将多音节歌词拆分为音节（`listening` `+` `+` -> `lis` `-ten` `-ing`）

## 示例
将歌声合成工程文件转换为五线谱（需要安装[musescore](https://musescore.org/)）
```py
import music21
import music21_svs_formats

music21_svs_formats.registAllFormats()

infile = "path_to_your_file.ustx"
project = music21.converter.parseFile(infile, forceSource=True, hyphenLang="en_US")
project.show()
```
