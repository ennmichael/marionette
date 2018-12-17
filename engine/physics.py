from __future__ import annotations

from typing import List

from engine.utils import Rectangle, normalized, point_in_rectangle


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

    def acceleration(self) -> complex:
        return self.force / self.mass

    def apply_force(self, f: complex) -> None:
        self.force += f

    def checkbox(self) -> Rectangle:
        return Rectangle.create(self.position, self.dimensions)


# TODO How difficult would it be to unit-test this class? I probably should
# Also, I shouldn't do collision checks randomly, I should only check entities close to the player
# So player should be a special entity, not just part of the list
class World:
    __slots__ = 'time_delta', 'gravity', 'drag', 'entities'

    def __init__(self, time_delta: float, gravity: float, drag: float, entities: List[Entity]):
        self.time_delta = time_delta
        self.gravity = gravity
        self.drag = drag
        self.entities = entities

    def update(self) -> None:
        self.update_physics()
        self.update_constraints()

    def update_physics(self) -> None:
        for e in self.entities:
            e.velocity += e.acceleration() + self.gravity * e.gravity_scale * 1j
            e.position += e.velocity
            e.force -= self.drag * normalized(e.force)

    def update_constraints(self) -> None:
        for solid_entity in self.solid_entities():
            for other_entity in self.entities:
                if other_entity is solid_entity:
                    continue
                World.solve_collision(solid_entity, other_entity)

    def solid_entities(self) -> List[Entity]:
        return [e for e in self.entities if e.solid]

    @staticmethod
    def solve_collision(solid_entity: Entity, other_entity: Entity) -> None:
        assert solid_entity.solid

        if other_entity.solid:
            raise NotImplementedError  # TODO: Meeting halfway once I have moving solid entities (if ever)
        else:
            # YOU CREATED A MONSTER
            solid_checkbox = solid_entity.checkbox()
            other_checkbox = other_entity.checkbox()
            upper_left_collided = point_in_rectangle(other_checkbox.upper_left, solid_checkbox)
            upper_right_collided = point_in_rectangle(other_checkbox.upper_right, solid_checkbox)
            lower_left_collided = point_in_rectangle(other_checkbox.lower_left, solid_checkbox)
            lower_right_collided = point_in_rectangle(other_checkbox.lower_right, solid_checkbox)
            if upper_right_collided and lower_right_collided:
                other_entity.velocity = other_entity.velocity.imag * 1j
                other_entity.position -= other_checkbox.upper_right.real - solid_checkbox.upper_left.real
            elif lower_left_collided and lower_left_collided:
                other_entity.velocity = other_entity.velocity.real
                other_entity.position -= other_checkbox.lower_left.imag - solid_checkbox.upper_left.imag
            elif upper_left_collided and lower_left_collided:
                other_entity.velocity = other_entity.velocity.imag * 1j
                other_entity.position += solid_checkbox.upper_right.real - other_checkbox.upper_left.real
            elif upper_right_collided and upper_left_collided:
                other_entity.velocity = other_entity.velocity.real
                other_entity.position += solid_checkbox.lower_left.imag - other_checkbox.upper_left.imag
            elif lower_right_collided:
                real_delta = other_checkbox.upper_left.real - solid_checkbox.upper_right.real
                imag_delta = other_checkbox.lower_left.imag - solid_checkbox.upper_left.imag
                if real_delta > imag_delta:
                    other_entity.velocity = other_entity.velocity.real
                    other_entity.position -= imag_delta * 1j
                else:
                    other_entity.velocity = other_entity.velocity.imag * 1j
                    other_entity.position -= real_delta
            elif lower_left_collided:
                real_delta = solid_checkbox.upper_right.real - other_checkbox.upper_left.real
                imag_delta = other_checkbox.lower_right.imag - solid_checkbox.upper_right.real
                if real_delta > imag_delta:
                    other_entity.velocity = other_entity.velocity.real
                    other_entity.position -= imag_delta * 1j
                else:
                    other_entity.velocity = other_entity.velocity.imag * 1j
                    other_entity.velocity += real_delta
            elif upper_left_collided:
                real_delta = solid_checkbox.lower_right.real - other_checkbox.lower_left.real
                imag_delta = solid_checkbox.lower_left.imag - other_checkbox.upper_left.imag
                if real_delta > imag_delta:
                    other_entity.velocity = other_entity.velocity.real
                    other_entity.position += imag_delta * 1j
                else:
                    other_entity.velocity = other_entity.velocity.imag * 1j
                    other_entity.position += real_delta
            elif upper_right_collided:
                real_delta = other_checkbox.upper_right.real - solid_checkbox.upper_left.real
                imag_delta = other_checkbox.upper_right.imag - solid_checkbox.lower_right.imag
                if real_delta > imag_delta:
                    other_entity.velocity = other_entity.velocity.real
                    other_entity.position += imag_delta * 1j
                else:
                    other_entity.velocity = other_entity.velocity.imag * 1j
                    other_entity.position -= real_delta
