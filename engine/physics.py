from __future__ import annotations

import enum
from typing import List

from engine.timer import Timer
from engine.utils import Rectangle, cross_product, complex_is_close


# TODO Use this
@enum.unique
class EntityKind(enum.Enum):
    SOLID = enum.auto()
    DYNAMIC = enum.auto()
    STATIC = enum.auto()


class Entity:
    __slots__ = 'position', 'dimensions', 'mass', 'force', 'velocity', 'solid', 'gravity_scale'

    def __init__(self, position: complex, dimensions: complex, mass: float,
                 solid: bool = False, gravity_scale: float = 1) -> None:
        self.position = position
        self.dimensions = dimensions
        self.mass = mass
        self.force = 0 + 0j
        self.velocity = 0 + 0j
        self.solid = solid
        self.gravity_scale = gravity_scale

    def update(self) -> None:
        pass

    def acceleration(self) -> complex:
        return self.force / self.mass

    def apply_force(self, f: complex) -> None:
        self.force += f

    @property
    def checkbox(self) -> Rectangle:
        return Rectangle(self.position, self.dimensions)


class TerrainBox(Entity):
    def __init__(self, position: complex, dimensions: complex) -> None:
        super().__init__(position, dimensions, mass=1, solid=True, gravity_scale=0)


Entities = List[Entity]


# TODO How difficult would it be to unit-test this class? I probably should
# Also, I shouldn't do collision checks randomly, I should only check entities close to the player
# So player should be a special entity, not just part of the list
# Perhaps this behaviour should be part of a camera class instead
class World:
    __slots__ = 'time_delta', 'gravity', 'drag', 'solid_entities', 'nonsolid_entities'

    def __init__(self, timer: Timer, time_delta: int, gravity: float, drag: float, entities: List[Entity]):
        timer.add_task(self.update, time_delta, repeat=True)
        self.time_delta = time_delta
        self.gravity = gravity
        self.drag = drag
        self.solid_entities = [e for e in entities if e.solid]
        self.nonsolid_entities = [e for e in entities if not e.solid]

    def update(self) -> None:
        for entity in self.nonsolid_entities:
            entity.velocity += entity.acceleration() + self.gravity * entity.gravity_scale * 1j
            entity.velocity -= self.drag * entity.velocity
            self.solve_collisions(entity)
            entity.force -= self.drag * entity.force
            entity.position += entity.velocity
            entity.update()

    def solve_collisions(self, dynamic_entity: Entity) -> None:
        # TODO Assert kind
        for solid_entity in self.solid_entities:
            World.solve_collision(dynamic_entity, solid_entity)

    @staticmethod
    def solve_collision(dynamic_entity: Entity, solid_entity: Entity) -> None:
        # TODO Assert kinds

        if dynamic_entity.velocity.real > 0:
            if dynamic_entity.velocity.imag < 0:
                if World.solve_vertical_collision(
                        dynamic_entity, solid_entity,
                        left=dynamic_entity.checkbox.upper_right,
                        right=dynamic_entity.checkbox.upper_right + dynamic_entity.velocity,
                        real=solid_entity.checkbox.left_real):
                    return
                World.solve_horizontal_collision(
                    dynamic_entity, solid_entity,
                    upper=dynamic_entity.checkbox.upper_right + dynamic_entity.velocity,
                    lower=dynamic_entity.checkbox.upper_right,
                    imag=solid_entity.checkbox.lower_imag)
            else:
                if World.solve_vertical_collision(
                        dynamic_entity, solid_entity,
                        left=dynamic_entity.checkbox.lower_right,
                        right=dynamic_entity.checkbox.lower_right + dynamic_entity.velocity,
                        real=solid_entity.checkbox.left_real):
                    return
                World.solve_horizontal_collision(
                    dynamic_entity, solid_entity,
                    upper=dynamic_entity.checkbox.lower_right,
                    lower=dynamic_entity.checkbox.lower_right + dynamic_entity.velocity,
                    imag=solid_entity.checkbox.upper_imag)
        else:
            if dynamic_entity.velocity.imag < 0:
                if World.solve_vertical_collision(
                        dynamic_entity, solid_entity,
                        left=dynamic_entity.checkbox.upper_left + dynamic_entity.velocity,
                        right=dynamic_entity.checkbox.upper_left,
                        real=solid_entity.checkbox.right_real):
                    return
                World.solve_horizontal_collision(
                    dynamic_entity, solid_entity,
                    upper=dynamic_entity.checkbox.upper_left + dynamic_entity.velocity,
                    lower=dynamic_entity.checkbox.upper_left,
                    imag=solid_entity.checkbox.lower_imag)
            else:
                if World.solve_vertical_collision(
                        dynamic_entity, solid_entity,
                        left=dynamic_entity.checkbox.lower_left + dynamic_entity.velocity,
                        right=dynamic_entity.checkbox.lower_left,
                        real=solid_entity.checkbox.right_real):
                    return
                World.solve_horizontal_collision(
                    dynamic_entity, solid_entity,
                    upper=dynamic_entity.checkbox.lower_left,
                    lower=dynamic_entity.checkbox.lower_left + dynamic_entity.velocity,
                    imag=solid_entity.checkbox.upper_imag)

    @staticmethod
    def solve_horizontal_collision(
            entity: Entity, solid_entity: Entity,
            upper: complex, lower: complex, imag: float) -> bool:
        assert complex_is_close(lower - upper, entity.velocity) or complex_is_close(upper - lower, entity.velocity)

        v1 = solid_entity.checkbox.left_real + imag * 1j - upper
        v2 = solid_entity.checkbox.right_real + imag * 1j - upper
        p1 = cross_product(v1, entity.velocity)
        p2 = cross_product(v2, entity.velocity)
        if p1 < 0 < p2 and upper.imag <= imag <= lower.imag:  # Second check fails
            entity.velocity -= (lower.imag - imag) * 1j
            entity.force = entity.force.imag * 1j
            return True
        return False

    @staticmethod
    def solve_vertical_collision(
            entity: Entity, solid_entity: Entity,
            left: complex, right: complex, real: float) -> bool:
        assert complex_is_close(left - right, entity.velocity) or complex_is_close(right - left, entity.velocity)

        v1 = real + solid_entity.checkbox.lower_imag * 1j - left
        v2 = real + solid_entity.checkbox.upper_imag * 1j - left
        p1 = cross_product(v1, entity.velocity)
        p2 = cross_product(v2, entity.velocity)
        if p1 < 0 < p2 and left.real <= real <= right.real:
            entity.velocity -= right.real - real
            entity.force = entity.force.real
            return True
        return False
