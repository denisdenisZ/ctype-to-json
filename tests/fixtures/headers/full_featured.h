#include <stdint.h>
#include <stdbool.h>

typedef enum {
    COLOR_RED,
    COLOR_GREEN,
    COLOR_BLUE,
} Color;

struct Point {
    int32_t x;
    int32_t y;
};

typedef struct {
    float r;
    float g;
    float b;
} Vec3;

typedef struct {
    uint8_t      u8;
    uint16_t     u16;
    uint32_t     u32;
    int32_t      i32;
    float        f32;
    double       f64;
    bool         flag;
    Color        color;
    struct Point point;
    Vec3         vec;
    int          numbers[4];
    Color        palette[3];
    struct Point *point_ptr;
    int          *int_ptr;
} Everything;
