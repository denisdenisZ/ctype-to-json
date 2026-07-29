#include <stdbool.h>
#include <stdint.h>


struct standard_types {
    bool var_bool;

    char var_char;
    signed char var_signed_char;
    unsigned char var_unsigned_char;

    short var_short;
    short int var_short_int;
    signed short var_signed_short;
    signed short int var_signed_short_int;
    unsigned short var_unsigned_short;
    unsigned short int var_unsigned_short_int;

    int var_int;
    signed var_signed;
    signed int var_signed_int;

    unsigned var_unsigned;
    unsigned int var_unsigned_int;

    long var_long;
    long int var_long_int;
    signed long var_signed_long;
    signed long int var_signed_long_int;

    unsigned long var_unsigned_long;
    unsigned long int var_unsigned_long_int;

    long long var_long_long;
    long long int var_long_long_int;
    signed long long var_signed_long_long;
    signed long long int var_signed_long_long_int;

    unsigned long long var_unsigned_long_long;
    unsigned long long int var_unsigned_long_long_int;

    float var_float;
    double var_double;
    long double var_long_double;
};

/* struct copy-assignment does member-wise assignment under the hood
 * meaning that because this struct has var_const_int it cannot be copy asigned
 */
struct qualifiers {
    const int var_const_int;
    volatile int var_volatile_int;
    const volatile int var_const_volatile_int;
};

struct fixed_width {
    int8_t  var_int8_t;
    int16_t var_int16_t;
    int32_t var_int32_t;
    int64_t var_int64_t;

    int_fast8_t  var_int_fast8_t;
    int_fast16_t var_int_fast16_t;
    int_fast32_t var_int_fast32_t;
    int_fast64_t var_int_fast64_t;

    int_least8_t  var_int_least8_t;
    int_least16_t var_int_least16_t;
    int_least32_t var_int_least32_t;
    int_least64_t var_int_least64_t;

    intmax_t var_intmax_t;
    intptr_t var_intptr_t;

    uint8_t  var_uint8_t;
    uint16_t var_uint16_t;
    uint32_t var_uint32_t;
    uint64_t var_uint64_t;

    uint_fast8_t  var_uint_fast8_t;
    uint_fast16_t var_uint_fast16_t;
    uint_fast32_t var_uint_fast32_t;
    uint_fast64_t var_uint_fast64_t;

    uint_least8_t  var_uint_least8_t;
    uint_least16_t var_uint_least16_t;
    uint_least32_t var_uint_least32_t;
    uint_least64_t var_uint_least64_t;

    uintmax_t var_uintmax_t;
    uintptr_t var_uintptr_t;
};

#include <wchar.h>

#if defined(__STDC_VERSION__) && __STDC_VERSION__ >= 201112L
#include <uchar.h>
#endif

struct wide {
    wchar_t   var_wchar_t;      // <wchar.h>

#if defined(__STDC_VERSION__) && __STDC_VERSION__ >= 201112L
    char16_t  var_char16_t;     // <uchar.h>
    char32_t  var_char32_t;     // <uchar.h>
#endif
};


#if defined(__STDC_VERSION__) && __STDC_VERSION__ >= 199901L
struct complex {
    float _Complex var_float_complex;
    double _Complex var_double_complex;
};
#endif

#if defined(__STDC_VERSION__) && __STDC_VERSION__ >= 201112L
#include <stdatomic.h>
struct atomic {
    _Atomic int var_atomic_int;
};

#include <stdalign.h>
struct alignment {
    _Alignas(16) int var_aligned_int;   // or alignas(16) via stdalign.h macro
};

struct nested {

    /* named type, named field - normal, nested access */
    struct struct_named_type_named_field {
        int var_named_type_named_field_struct;
    } var_named_type_named_field_struct_holder;

    /* anonymous type, named field - nested access, type unreferenceable elsewhere */
    struct {
        int var_anon_type_named_field_struct;
    } var_anon_type_named_field_struct_holder;

    /* anonymous type, unnamed field - fully transparent */
    struct {
        int var_anon_type_unnamed_field_struct;
    };

    union union_named_type_named_field {
        int var_named_type_named_field_union_int;
        float var_named_type_named_field_union_float;
    } var_named_type_named_field_union_holder;

    union {
        int var_anon_type_named_field_union_int;
        float var_anon_type_named_field_union_float;
    } var_anon_type_named_field_union_holder;

    union {
        int var_anon_type_unnamed_field_union_int;
        float var_anon_type_unnamed_field_union_float;
    };

    enum enum_named_type_named_field {
        VAR_NAMED_TYPE_NAMED_FIELD_ENUM_A,
        VAR_NAMED_TYPE_NAMED_FIELD_ENUM_B
    } var_named_type_named_field_enum_holder;

    enum {
        VAR_ANON_TYPE_NAMED_FIELD_ENUM_A,
        VAR_ANON_TYPE_NAMED_FIELD_ENUM_B
    } var_anon_type_named_field_enum_holder;
};
#endif

#include <stddef.h>

struct plat_specific {
    size_t var_size_t;
    ptrdiff_t var_ptrdiff_t;
};

enum enum_type {
    ENUM_VAL_0,
    ENUM_VAL_1,
    ENUM_VAL_2,
};

union union_type {
    int i;
    float f;
};

struct nested_types {

    enum enum_type var_enum;

    struct fixed_width var_fixed_width_struct;

    union union_type var_union;

};

struct opaque_handle;

struct pointer_variants {
    int *var_int_pointer;
    int **var_int_pointer_pointer;

    const char *var_ptr_to_const;

    int var_int_array[10];
    int var_int_array_array[10][10];

    int        *var_pointer_array[10];
    int        (*var_array_pointer)[10];
    int        (*var_func_pointer_args)(int, char);

    void (*var_func_pointer)(void);
    int (*var_variadic_func_ptr)(int, ...);

    struct opaque_handle *var_opaque_pointer;

    struct { int x; } *var_pointer_to_anon_struct;
    union { int x; } *var_pointer_to_anon_union;
};

struct flexible_array {
    /* Has to be last member */
    /* Cannot be a member of another struct, except if it is the last memeber */
    /* Cannot be member of array */
    /* var_flexible_array will be excluded from sizeof(struct flexible_array) */
    /* Must be allocated with malloc(sizeof(struct flexible_array) + n * sizeof(int)) and manually freed*/
    int var_flexible_array[];
};

struct bitfields {
    unsigned int var_bitfield_1  : 1;
    unsigned int var_bitfield_3  : 3;
    unsigned int var_bitfield_12 : 12;

    /* signed bitfields are allowed, but sign behavior on the top bit is implementation-defined pre-C23 */
    int          var_signed_bitfield : 4;

    /* unnamed, zero-width - forces next field to start a new allocation unit */
    unsigned int : 0;

    unsigned int var_after_boundary : 5;

    /* unnamed, nonzero-width - just padding, no accessible name */
    unsigned int : 4;

    /* C23 allows bool as a bitfield base type explicitly; earlier standards - implementation defined/extension */
    bool         var_bool_bitfield : 1;
};

#if defined(__STDC_VERSION__) && __STDC_VERSION__ >= 202311L
struct c23_types {
    nullptr_t   var_nullptr_t;

#if defined(__STDC_BITINT_MAXWIDTH__)
    _BitInt(24) var_bitint;
    unsigned _BitInt(24) var_ubitint;
#endif

#if defined(__STDC_IEC_60559_DFP__)
    _Decimal32  var_decimal32;
    _Decimal64  var_decimal64;
    _Decimal128 var_decimal128;
#endif
};
#endif

typedef int my_int_t;
typedef my_int_t another_int_t;
typedef unsigned int my_uint_t;
typedef struct standard_types standard_types_t;
typedef enum enum_type enum_type_t;
typedef int* IntPtr;
typedef int int_array10_t[10];
typedef int (*func_ptr_t)(int, char);
typedef int (*array_ptr_t)[10];

typedef struct {
    int x;
    int y;
} typedefed_anon_struct;

typedef struct typedefed_named_struct_name {
    int x;
    int y;
} typedefed_named_struct_typedef;

struct uses_typedefed_type {
    typedefed_anon_struct var_typedefed_anon_struct;
    typedefed_named_struct_typedef var_typedefed_named_struct_typedef;
    struct typedefed_named_struct_name var_typedefed_named_struct_name;

    my_int_t       var_my_int_t;
    my_uint_t      var_my_uint_t;
    standard_types_t var_standard_types_t;
    enum_type_t    var_enum_type_t;
    int_array10_t  var_int_array10_t;
    func_ptr_t     var_func_ptr_t;
    array_ptr_t    var_array_ptr_t;
    another_int_t var_another_int_t;
    IntPtr        var_IntPtr;
};

