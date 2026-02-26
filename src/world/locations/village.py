
width =40
height = 40

layer_water = [[0 for _ in range(width)] for _ in range(height)]

layer_ground = [[None for _ in range(width)] for _ in range(height)]

for y in range(height):
    for x in range(width):
        layer_ground[y][x] = 1

path_x = width // 2
for y in range(height):
    layer_ground[y][path_x] = 3
    layer_ground[y][path_x + 1] = 3

layer_ground[height - 1][path_x] = 9
layer_ground[height - 1][path_x + 1] = 9

layer_objects = [[None for _ in range(width)] for _ in range(height)]

import random

for y in range(height):
    for x in range(width):
        if abs(x - path_x) > 5:
            if random.random() < 0.2:
                layer_objects[y][x] = 5

map_data = {
    "water": layer_water,
    "ground": layer_ground,
    "objects": layer_objects
}
