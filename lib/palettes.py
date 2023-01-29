color = {
    'white': (255, 255, 255),
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'cyan': (0, 255, 255),
    'magenta': (255, 0, 255),
}

# 16 colors - # white + primary, and secondary colors repeated
palette_16 = (
    color['white'],
    color['red'],
    color['green'],
    color['blue'],
    color['yellow'],
    color['cyan'],
    color['magenta'],
    color['red'],
    color['green'],
    color['blue'],
    color['yellow'],
    color['cyan'],
    color['magenta'],
    color['red'],
    color['green'],
    color['blue'],
)

# 6 colors - primary and secondary
palette_6 = (
    color['red'],
    color['yellow'],
    color['green'],
    color['cyan'],
    color['blue'],
    color['magenta'],
)

# 12 colors - primary and secondary colors repeated
palette_12 = (
    color['red'],
    color['green'],
    color['blue'],
    color['yellow'],
    color['cyan'],
    color['magenta'],
    color['red'],
    color['green'],
    color['blue'],
    color['yellow'],
    color['cyan'],
    color['magenta'],
)

# major scale notes
in_key = color['white']
out_key = color['red']
palette_key = (
    in_key,
    out_key,
    in_key,
    out_key,
    in_key,
    in_key,
    out_key,
    in_key,
    out_key,
    in_key,
    out_key,
    in_key
)
