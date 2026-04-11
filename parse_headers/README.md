# C Header Parser — User Guide

## What it does

This tool parses C header files and produces a JSON description of all structs and enums found within them, including field names, types, byte offsets, and sizes. It works by parsing the header with libclang to extract type information, then compiling and running a small probe program to get the real offsets and sizes for your target platform.

---

## Basic usage

```
python produce_json.py [options] header_file.h
```

The simplest invocation with a config file:

```
python produce_json.py -c config.toml my_types.h
```

This parses `my_types.h`, probes offsets and sizes on the current machine, and prints the result as JSON to stdout.

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
# C standard to use: "11", "99", or "17"
c_standard = "11"
```

`toolchain.cc` is required. Everything else is optional.

The header file's own directory is always added to the include paths automatically, so you don't need to add it manually.

---

## Options

| Option | Description |
|--------|-------------|
| `header_file.h` | The header file to parse (required) |
| `-c`, `--config FILE` | Path to TOML config file |
| `-o`, `--output FILE` | Write JSON output to a file instead of stdout |
| `--DEBUG` | Print debug information (args, config) before running |
| `--emit-prober` | Build the size prober but don't run it (for cross compilation) |
| `--sizes FILE` | Skip probing, use a precomputed sizes file instead |
| `--no-probe` | Skip probing entirely, output only the parsed type information without offsets or sizes |

`--emit-prober`, `--sizes`, and `--no-probe` are mutually exclusive.

---

## Cross compilation

If you are targeting a different architecture than the machine you are running on, the prober can't be run locally. The workflow is:

**Step 1** — Generate the prober binary on your host machine:

```
python produce_json.py -c config.toml --emit-prober my_types.h
```

This writes `size_prober` to the current directory (or to `--output` if specified).

**Step 2** — Copy `size_prober` to the target machine and run it, saving the output:

```
./size_prober > sizes.txt
```

**Step 3** — Back on the host, feed the output back in:

```
python produce_json.py -c config.toml --sizes sizes.txt my_types.h
```

---

## Output format

The output is a JSON object keyed by an internal hash. Each entry is either a struct or an enum.

### Struct

```json
{
  "name": "AecConfig",
  "kind": "struct",
  "size": 44,
  "fields": [
    {
      "name": "mode",
      "kind": "field",
      "type": "AecMode",
      "ref": 1234567890,
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
      "type": "AecConfig",
      "pointer": true,
      "ref": 1234567890,
      "offset": 48,
      "size": 8
    }
  ]
}
```

### Enum

```json
{
  "name": "AecMode",
  "kind": "enum",
  "fields": [
    { "name": "AEC_MODE_AUTO", "type": "AecMode", "value": 0 },
    { "name": "AEC_MODE_MANUAL", "type": "AecMode", "value": 1 }
  ]
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
| `ref` | Present if the type is another user-defined type — the hash key of its entry |
| `array` | Present for array fields — list of dimensions, e.g. `[5]` or `[3, 5]` for 2D |
| `pointer` | Present and `true` if the field is a pointer |

---

## Currently unsupported field types

The tool will exit with a clear error message if it encounters any of the following in a struct:

- Bitfields (`uint8_t x : 4`)
- Union fields
- Anonymous nested structs/unions
- Function pointers

These are planned for future support. Non-struct top-level declarations (function prototypes, macros, etc.) are silently ignored.
