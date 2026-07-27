#include <stdint.h>
#include <stdbool.h>

#include "included.h"
#include "window_cfg.h"

/* --- Enums --- */

typedef enum {
    CONTROL_MODE_AUTO,
    CONTROL_MODE_MANUAL,
    CONTROL_MODE_SHUTTER_PRIORITY,
    CONTROL_MODE_GAIN_PRIORITY,
} ControlMode;

typedef enum {
    FILTER_MODE_AUTO,
    FILTER_MODE_DAYLIGHT,
    FILTER_MODE_CLOUDY,
    FILTER_MODE_TUNGSTEN,
    FILTER_MODE_FLUORESCENT,
} FilterMode;

/* --- Nested structs --- */

typedef struct {
    uint32_t min_us;
    uint32_t max_us;
    uint32_t step_us;
} ValueRange;

typedef struct {
    float min_db;
    float max_db;
    float step_db;
} ScaleRange;

/* --- Named (non-typedef) struct --- */

struct RegionRect {
    uint16_t x;
    uint16_t y;
    uint16_t width;
    uint16_t height;
};

/* --- Top level configs --- */

typedef struct {
    ControlMode       mode;
    uint32_t      target_value;
    uint32_t      value_us;
    float         scale_db;
    ValueRange value_range;
    ScaleRange     scale_range;
    bool          enabled;
    uint8_t       update_speed;
} ControlConfig;

#define ARR_SIZE 5

typedef struct {
    FilterMode  mode;
    uint32_t filter_temp;
    float    r_gain;
    float    gr_gain;
    float    gb_gain;
    float    b_gain;
    bool     enabled;
    int      gains[ARR_SIZE];
    int      gains2d[5][4];
    int      gains3d[5][4][3];
    FilterMode  filter_table[5];
} FilterConfig;

typedef struct {
    uint8_t        frame_rate;
    uint16_t       hblank;
    uint16_t       vblank;
    uint8_t        num_exposures;
    struct RegionRect roi;
    ControlConfig      aec;
    FilterConfig      awb;
    FilterConfig      *pointer;
} DeviceConfig;

struct i_include {
    struct included_struct included;
    window window;
};

union some_union {
    int a;
    bool b;
};

void some_function(void *);
