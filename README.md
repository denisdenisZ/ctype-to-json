# ctype-to-json — User Guide

## What it does

This tool parses C header files and produces a JSON description of all structs and enums found within them, including field names, types, byte offsets, and sizes. It works by parsing the headers with libclang to extract type information, then compiling and running a small probe program to get the real offsets and sizes for the target platform.

---

## Installation

```
pip install -e .
```

This installs the `ctype-to-json` command along with its dependencies.

---

## Basic usage

```
ctype-to-json [options] header_file.h [header_file2.h ...]
```

The simplest invocation with a config file:

```
ctype-to-json -c config.toml my_types.h
```

Multiple headers can be passed at once:

```
ctype-to-json -c config.toml types_a.h types_b.h
```

All types from all headers are merged into a single JSON output. Overlapping includes (e.g. two headers that both include `stdint.h`) are handled automatically — shared types are only processed once.

---

## Config file

The config file is a TOML file. Example:

```toml
[toolchain]
cc = "gcc"
# Flags passed to the compiler when building the size prober
flags = []
# System include directories (e.g. sysroot includes for cross compilation)
include_dirs = []

[parser]
# supported C standards (ones i've tested): "11", "99", or "17"
c_standard = "11"
```

The directory of each header file is always added to the include paths automatically, so you don't need to add them manually.

---

## Options

| Option | Description |
|--------|-------------|
| `header_file.h ...` | One or more header files to parse (required) |
| `-c`, `--config FILE` | Path to TOML config file |
| `-o`, `--output FILE` | Write JSON output to a file instead of stdout |
| `--DEBUG` | Print debug information (args, config) before running |
| `--emit-prober` | Build the size prober but don't run it (for cross compilation) |
| `--sizes FILE` | Skip probing, use a precomputed sizes file instead |
| `--no-probe` | Skip probing entirely, output only parsed type information without offsets or sizes |

`--emit-prober`, `--sizes`, and `--no-probe` are mutually exclusive.

---

## Cross compilation

If you are targeting a different architecture than the machine you are running on, the prober can't be run locally. The workflow is:

**Step 1** — Generate the prober binary on your host machine:

```
ctype-to-json -c config.toml --emit-prober my_types.h
```

This writes `size_prober` to the current directory (or to `--output` if specified).

**Step 2** — Copy `size_prober` to the target machine and run it, saving the output:

```
./size_prober > sizes.txt
```

**Step 3** — Back on the host, feed the output back in:

```
ctype-to-json -c config.toml --sizes sizes.txt my_types.h
```

---

## Output format

The output is a JSON object keyed by the C type name. Typedef structs use the typedef name as the key (e.g. `"ControlConfig"`). Non-typedef structs include the `struct` keyword (e.g. `"struct RegionRect"`). This ensures keys are valid C type names and can be used directly in code generation. The name inside the json object is stripped of the struct keyword!

Each entry is either a struct, enum, or the special `meta` entry.

### Metadata

```json
{
  "meta": {
    "kind": "metadata",
    "headers": [
      "/path/to/my_types.h",
      "/usr/include/stdint.h"
    ]
  }
}
```

### Struct

```json
{
  "ControlConfig": {
    "name": "ControlConfig",
    "kind": "struct",
    "size": 44,
    "fields": [
      {
        "name": "mode",
        "kind": "field",
        "type": "ControlMode",
        "ref": "ControlMode",
        "offset": 0,
        "size": 4
      },
      {
        "name": "enabled",
        "kind": "field",
        "type": "bool",
        "offset": 40,
        "size": 1
      },
      {
        "name": "gains",
        "kind": "field",
        "type": "int",
        "array": [5],
        "offset": 28,
        "size": 20
      },
      {
        "name": "ptr",
        "kind": "field",
        "type": "FilterConfig",
        "pointer": true,
        "ref": "FilterConfig",
        "offset": 48,
        "size": 8
      }
    ]
  }
}
```

### Enum

```json
{
  "ControlMode": {
    "name": "ControlMode",
    "kind": "enum",
    "fields": [
      { "name": "CONTROL_MODE_AUTO", "type": "ControlMode", "value": 0 },
      { "name": "CONTROL_MODE_MANUAL", "type": "ControlMode", "value": 1 }
    ]
  }
}
```

### Field properties

| Property | Description |
|----------|-------------|
| `name` | Field name |
| `kind` | Always `"field"` |
| `type` | C type name (primitive, typedef name, or `struct Foo`) |
| `offset` | Byte offset within the struct |
| `size` | Size in bytes |
| `ref` | Present if the type is another user-defined type — matches the top-level key of its entry in the JSON |
| `array` | Present for array fields — list of dimensions, e.g. `[5]` or `[3, 5]` for 2D |
| `pointer` | Present and `true` if the field is a pointer |

The `ref` value always matches the top-level key of the referenced type, so lookups are direct: `json[field["ref"]]`.

---

## Currently unsupported field types

The tool will exit with an error message if it encounters any of the following as a field in a struct:

- Bitfields (`uint8_t x : 4`)
- Union fields

These are planned for future support. Non-struct top-level declarations (function prototypes, macros, etc.) are silently ignored.

> **Known gap:** anonymous nested structs/unions and function-pointer fields are meant to be
> rejected the same way, but the detection in `is_unsupported` currently misses both (function
> pointers look like plain pointers; anonymous nested structs get emitted as an extra synthetic
> top-level entry instead of being flagged). Tracked as follow-up work, not yet fixed.

---

## Development

Install with the `dev` extra and run the test suite with pytest:

```
pip install -e ".[dev]"
pytest
```

Tests that compile and run the size prober are skipped automatically if `gcc` isn't available.
Test fixtures (sample headers and configs) live under `tests/fixtures/`.
