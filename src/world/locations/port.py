
width =40
height = 40

layer_water = [[0 for _ in range(width)] for _ in range(height)]

layer_ground = [[None for _ in range(width)] for _ in range(height)]

for y in range(height):
    for x in range(width):
        if y < 25:
            layer_ground[y][x] = 1
        elif y == 25:
            layer_ground[y][x] = 4

pier_x = width // 2
pier_start_y = 25
pier_end_y = 35

for y in range(pier_start_y, pier_end_y):
    for x in range(pier_x - 2, pier_x + 3):
        layer_ground[y][x] = 2

for x in range(pier_x - 6, pier_x + 7):
    layer_ground[pier_end_y][x] = 2
    layer_ground[pier_end_y + 1][x] = 2

for y in range(0, 25):
    layer_ground[y][pier_x] = 3
    layer_ground[y][pier_x + 1] = 3

layer_ground[0][pier_x] = 9
layer_ground[0][pier_x + 1] = 9

layer_objects = [[None for _ in range(width)] for _ in range(height)]

import random

random.seed(42)

for y in range(25):
    for x in range(width):
        if layer_ground[y][x] == 1:

            if abs(x - pier_x) > 3:
                if random.random() < 0.1:
                    layer_objects[y][x] = 5

layer_objects[30][pier_x - 1] = 6
layer_objects[32][pier_x + 2] = 6
layer_objects[35][pier_x - 4] = 6
layer_objects[35][pier_x + 5] = 6

map_data = {
    "water": layer_water,
    "ground": layer_ground,
    "objects": layer_objects
}
