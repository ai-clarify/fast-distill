# Copyright 2026 cklxx
#
# Licensed under the MIT License.


def final_velocity(initial_velocity: float, acceleration: float, time: float) -> int:
    """Calculates the final velocity of an object given its initial velocity, acceleration, and time.

    Args:
        initial_velocity: The initial velocity of the object.
        acceleration: The acceleration of the object.
        time: The time elapsed.

    Returns:
        The final velocity
    """
    return initial_velocity + acceleration * time
