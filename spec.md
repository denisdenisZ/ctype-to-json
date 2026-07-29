# Top level
```json
    "target": {},
    "structs": {},
    "unions": {},
    "enums": {},
    "numeric": {},
    "bool": {},
```

# Target block
```json
    "target": {
        "endianess": "",
        "int_representation": "",
        "float_format": "",
        "data_model": "",
        "pointer_bits": 0,
    },
```
- **`endianess`** - `little` or `big`
- **`int_representation`** - `twos_complement` only for now
- **`float_format`** - `ieee754` only for now
- **`data_model`**
	- `LP64` - Linux/MacOS x86_64
	- `LLP64` - Windows x86_64
	- `ILP32` - x86/ARM 32 bit
- **`pointer_bits`** - present here in case no pointer types are defined

# Structs block
```json
"structs": {
	"cursor.spelling": {
		"name": "",
		"kind": "struct",
		"size_bits": 0,
		"align_bytes": 0,
		"fields": [],
	},
},
```
- **`cursor.spelling`** - Based on the fact that we only collect top level definitions only of **structs**, **enums** and **unions** from a single translation unit, this is guaranteed to be unique per C standard. Pythons `cindex.Cursor.spelling()` function gives us that unique name.
- **`kind`** - always **struct** at this level, here for consistency, being able to check for kind on all objects.
- **`size_bits`** - size in bits
- **`align_bytes`** - alignment requirement for type, in **bytes**
- **`fields`** - a list of field objects

## Field objects
Here depending on kind different fields are present.

### Numeric field
```json
{
	"name": "",
	"kind": "numeric_field",
	"ref": ""
},
```
- **`ref`** - holds a key from the numeric list.

### Bool field
```json
{
	"name": "",
	"kind": "bool_field",
	"ref": "",
},
```
**`ref`** - holds a key from the bool list, should be one single entry.

### Enum field
```json
{
	"name": "",
	"kind": "enum_field",
	"ref": "",
}
```
- **`name`** - name here can never be null, although it compiles a filed with no name of type anonymous enum produces a no op. (**TODO** check standard!)
- **`ref`** - here is a valid key from the top level **enums** list. If the enum is anonymous the ref name will be auto generated and the definition will be hoisted to the enums top level list. It will follow the format `__anon_enum_HASH` where `HASH` will be of format **TODO**.

### Struct field
```json
{
	"name": "",
	"kind": "struct_field",
	"ref": "",
}
```
- **`name`** - if no name is provided for the field it is `null`
- **`ref`** follows the same rules as for enums

### Union field
```json
{
	"name": "",
	"kind": "union_field",
	"ref": "",
}
```
Same rules apply as structs fields.

### Array field
```json
{
	"name": "",
	"kind": "array_field",

	"incomplete": false,

	"count": 0,
	"element": {
		"kind": "array_field",
		"incomplete": false,
		"count": 0,

		"element": {
			"kind": "numeric_field",
			"ref": "",
		}
	},

	"size_bits": 0,

	"offset_bits": 0,
	"align_bytes": 0,
}
```

### Pointer field
```json
{
	"name": "",
	"kind": "pointer_field",
	"pointee": {
		"kind": "",
	},
}
```

### Function pointer field
```json
{
	"name": "",
	"kind": "func_pointer_field",
}
```
We only care about the space they take, nothing else.

### Complex field
Currently unsuported

### Bitfield field
```json
{
	"name": "",
	"kind": "bitfield_field",
	"ref": "",
	"width": "",
}
```
- **`name`** - could be null for anonymous bit field

# Enums block
```json
"enums": {
	"cursor.spelling": {
		"name": "",
		"kind": "enum",
		"c_type": "",
		"underlying_type": "",

		"enumerators": [
			{
				"name": "",
				"value": "",
			},
		]
	}
},
```
- **`underlying_type`** - is a ref to the numeric list

# Unions block
```json
"unions": {
	"cursor.spelling": {
		"name": "",
		"kind": "union",
		"size_bits": 0,
		"align_bytes": 0,
		"fields": [],
	},
},
```
Each fields offset here should be 0

# Numerics block
```json
"numerics": {
	"type.spelling": {
		"name": "",
		"kind": "numeric",
		"c_type": "unsigned int",

		"size_bits": 0,
		"align_bytes": 0,
		"is_signed": false,

		"is_float": false,
	}
}
```

# Bool block
```json
"bool": {
	"type.spelling" {
		"name": "",
		"kind": "bool",
		"c_type": "_Bool",

		"size_bits": 0,

		"offset_bits": 0,
		"align_bytes": 0,
	}
},
```
