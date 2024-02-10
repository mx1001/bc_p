from mathutils import Vector


def increment_round(value, increment, size=8):
    amount = round(increment, size)
    split = str(amount).split('.')[1]
    length = len(split) if amount != 0 else 0

    return round(round(value / amount) * amount, length)


def increment_round_2d(x, y, increment, min_limit=False):
    _x = float(x)

    limit = increment

    x = increment_round(x, increment)
    if min_limit:
        if _x < 0:
            limit = -limit
        if x == 0:
            x += limit

    y = increment_round(y, increment)
    if min_limit:
        if y == 0:
            y += limit

    return x, y

def coordinate_overlap2d(location1, location2, size=1):
    return (location1 - location2).length < size


def vector_sum(vectors):
    return sum(vectors, Vector())


def coordinates_center(coordinates):
    return vector_sum((Vector(coord) for coord in coordinates)) / len(coordinates)


def coordinates_dimension(coordinates):
    x = [coord[0] for coord in coordinates]
    y = [coord[1] for coord in coordinates]
    z = [coord[2] for coord in coordinates]

    return  Vector((max(x), max(y), max(z))) - Vector((min(x), min(y), min(z)))


def coordinate_bounds(coordinates):
    x =[c[0] for c in coordinates]
    y =[c[1] for c in coordinates]
    z =[c[2] for c in coordinates]

    current_x = lambda i: min(x) if i < 4 else max(x)
    current_y = lambda i: min(y) if i in {0, 1, 4, 5} else max(y)
    current_z = lambda i: min(z) if i in {0, 3, 4, 7} else max(z)

    return [Vector((current_x(i), current_y(i), current_z(i))) for i in range(8)]
