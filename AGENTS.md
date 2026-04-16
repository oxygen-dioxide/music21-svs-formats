# AGENTS.md - Agent Developer Guidelines

This file provides guidance for AI agents operating in the music21-svs-formats repository.

## Project Overview

music21-svs-formats provides support for singing voice synthesis (SVS) file formats in music21 via the LibreSVIP library. It enables conversion between music21.stream.Score and various SVS formats (USTX, VOCALOID, DeepVocal, etc.).

## Build/Lint/Test Commands

### Running Tests

```bash
# Run all tests
pytest

# Run a single test file
pytest tests

# Run a single test
pytest tests/test_parser.py::test_external_midi_parse -v

# Run tests with coverage
coverage run --source=src -m pytest tests
```

### Type Checking

```bash
# Run mypy (configured in pyproject.toml)
mypy src/
```

### Formatting

```bash
# Formatting code with ruff
ruff format
```

### Development Installation

```bash
# Install libreSVIP development version (PyPI v2.3.1 has a bug that causes tests to fail, fixed in dev)
pip install git+https://github.com/SoulMelody/LibreSVIP@6f58fd611aa83134e588bde10610f7e80558dda8

# Install in editable mode with test dependencies
pip install -e ".[test]"

```

### VS Code Integration

The project is configured for pytest in `.vscode/settings.json`. Tests can be run from the Test Explorer.

## Code Style Guidelines

### Imports

Organize imports in the following order (per PEP 8 with modifications):
1. Standard library (`pathlib`, `copy`, `warnings`)
2. Third-party packages (`music21`, `libresvip`, `types_linq`, `more_itertools`)
3. Local imports (`from music21_svs_formats import ...`)

Use explicit relative imports for local packages:
```python
from music21_svs_formats import parser
from music21_svs_formats import generator
```

### Type Hints

Use Python 3.10+ union syntax for type hints:
```python
def parseFile(
    self, filePath: str | pathlib.Path, number: Optional[int] = None, **keywords
) -> music21.stream.Score:
```

Import types from `typing` explicitly:
```python
from typing import List, Tuple, Dict, Optional
```

### Naming Conventions

- **Functions/variables**: snake_case (`parseProject`, `mScore`)
- **Classes**: PascalCase (`LibresvipSubConverter`, `ConverterException`)
- **Constants**: SCREAMING_SNAKE_CASE (`RESOLUTION = 480`)
- **Type variables**: PascalCase (e.g., using `type[...]` for creating types at runtime)

### Function/Class Docstrings

Include docstrings for public functions and classes:
```python
def parseProject(lProject: libresvip.model.base.Project) -> music21.stream.Score:
    """
    Convert a LibreSVIP Project to a music21 Score.
    
    Args:
        lProject: The LibreSVIP project to convert.
        
    Returns:
        A music21.stream.Score object.
    """
```

### Error Handling

- Use custom exceptions that inherit from music21 exceptions where appropriate
- Raise `ValueError` for invalid arguments or unsupported formats
- Use `warnings.warn()` for non-fatal issues (e.g., format not registered in music21)

### File Organization

Source code structure:
```
src/music21_svs_formats/
  __init__.py      # Main entry point, registration functions
  parser.py        # LibreSVIP -> music21 conversion
  generator.py    # music21 -> LibreSVIP conversion
  converter.py   # music21 SubConverter implementation
  util.py         # Constants and utilities
```

Test files mirror the source structure:
```
tests/
  test_parser.py
  test_generator.py
  test_regist.py
  utils.py         # Shared fixtures
```

### Testing Patterns

Use pytest fixtures from `tests/utils.py`:
```python
@pytest.fixture
def midi_converter():
    return music21_svs_formats.getSubConverterByFormat("mid")()

@pytest.fixture
def env():
    return music21.environment.Environment()
```

Use parametrize for multiple test cases:
```pytest.mark.parametrize("file_name", ["music21-test01.mid"])```

### Code Patterns

#### Creating Dynamic Classes

The project uses `types.new_class` for dynamic SubConverter creation (see `__init__.py`):
```python
return types.new_class(
    "libresvip_" + format,
    (LibresvipSubConverter,),
    {},
    lambda ns: ns.update({...}),
)
```

#### Using Enumerable

The project uses `types_linq.Enumerable` for functional-style operations:
```python
from types_linq import Enumerable

result = (
    Enumerable(items)
    .select(lambda x: x.field)
    .where(lambda x: x > 0)
    .to_list()
)
```

#### music21 Integration

Implement `LibresvipSubConverter` extending `music21.converter.subConverters.SubConverter`:
```python
class LibresvipSubConverter(music21.converter.subConverters.SubConverter):
    extension: str = ""
    plugin_object: libresvip.extension.base.SVSConverter
```

## Key Dependencies

- `music21`: Music notation library
- `libresvip`: SVS file format library
- `types_linq`: Functional programming extensions
- `more_itertools`: Additional itertools utilities
- `pydantic.mypy`: Type checking for pydantic models

## Common Tasks

### Adding Support for a New Format

1. Register the format with `music21_svs_formats.registFormat(format_name)`
2. The converter will be automatically created via `LibresvipSubConverter`

### Running Round-Trip Tests

Test parsing and generating to ensure bidirectional conversion works:
```python
def test_roundtrip(midi_converter, env):
    # Parse
    m_score = midi_converter.parseFile(original_file)
    # Generate
    midi_converter.write(m_score, "midi", fp=output_file)
```

### Key Resolution

The parser applies key detection and transposition to match music21's key-aware processing:
```python
try:
    key = mScore.analyze("key")
    applyKey(mScore, key)
except music21.analysis.discrete.DiscreteAnalysisException:
    pass  # Key detection failed, continue without key
```

## Notes

- The project uses a resolution of 480 ticks per quarter note (`util.RESOLUTION`)
- LibreSVIP model objects are imported from `libresvip.model.base`
- SVS converter plugins are managed via `libresvip.extension.manager.plugin_manager`