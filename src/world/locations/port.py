import random

width = 65
height = 40

layer_water = [[0 for _ in range(width)] for _ in range(height)]

layer_ground = [[0 for _ in range(width)] for _ in range(height)]

layer_objects = [[0 for _ in range(width)] for _ in range(height)]


coast_y = 20
road_x = 32

for y in range(height):
    for x in range(width):
        if y < coast_y:
            layer_ground[y][x] = 1
        # Берегова лінія
        elif y == coast_y:
            layer_ground[y][x] = 4

for y in range(0, coast_y + 1):
    layer_ground[y][road_x] = 3
    layer_ground[y][road_x + 1] = 3

layer_ground[0][road_x] = 9
layer_ground[0][road_x + 1] = 9


pier_start_y = coast_y + 1
pier_turn_y = 32
pier_end_x = road_x + 15

for y in range(pier_start_y, pier_turn_y + 1):
    for x in range(road_x - 1, road_x + 3):
        layer_ground[y][x] = 2

for x in range(road_x - 1, pier_end_x):
    for y in range(pier_turn_y - 1, pier_turn_y + 2):
        layer_ground[y][x] = 2


building_x = road_x + 8
building_y = 5
building_w = 12
building_h = 8

for y in range(building_y, building_y + building_h):
    for x in range(building_x, building_x + building_w):
        layer_objects[y][x] = 7 # Код будівлі


boat_x = road_x + 3
boat_y = 26
layer_objects[boat_y][boat_x] = 6


random.seed(42)

for y in range(coast_y):
    for x in range(width):
        if layer_ground[y][x] == 3: continue
        if layer_objects[y][x] == 7: continue

        if building_x - 2 <= x <= building_x + building_w + 2 and building_y - 2 <= y <= building_y + building_h + 2:
            continue

        if random.random() < 0.08:
            layer_objects[y][x] = 5


map_data = {
    "water": layer_water,
    "ground": layer_ground,
    "objects": layer_objects
}
