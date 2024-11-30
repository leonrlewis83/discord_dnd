import random


def roll_3d6():
    return sum(random.randint(1, 6) for _ in range(3))

def generate_grid():
    return [roll_3d6() for _ in range(9)]