typedef struct {
    int a;
    union {
        int as_int;
        float as_float;
    } u;
    int b;
} struct_with_union_field;
