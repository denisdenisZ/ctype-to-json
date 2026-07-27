#include "unsupported_union.h"

typedef struct {
    struct_with_union_field inner;
    int c;
} wraps_unsupported;
