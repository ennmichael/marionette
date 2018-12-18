from __future__ import annotations

import enum
from typing import List

from engine.sdl import get_current_time
from engine.utils import Rectangle, Line, Corner


# TODO Use this
@enum.unique
class EntityKind(enum.Enum):
    DYNAMIC = enum.auto()
    STATIC = enum.auto()
    SOLID = enum.auto()


class Entity:
    __slots__ = 'position', 'dimensions', 'mass', 'force', 'velocity', 'kind', 'gravity_scale'

    def __init__(
            self, position: complex, dimensions: complex, mass: float,
            kind: EntityKind = EntityKind.DYNAMIC, gravity_scale: float = 1) -> None:
        self.position = position
        self.dimensions = dimensions
        self.mass = mass
        self.force = 0 + 0j
        self.velocity = 0 + 0j
        self.kind = kind
        self.gravity_scale = gravity_scale

    def update(self) -> None:
        pass

    def physics_update(self) -> None:
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
        super().__init__(position, dimensions, mass=1, kind=EntityKind.SOLID, gravity_scale=0)


Entities = List[Entity]


# TODO How difficult would it be to unit-test this class? I probably should
# Also, I shouldn't do collision checks randomly, I should only check entities close to the player
# So player should be a special entity, not just part of the list
# Perhaps this behaviour should be part of a camera class instead
class World:
    __slots__ = (
        'timestep_milliseconds', 'timestep_seconds', 'time_accumulator', 'last_update_time',
        'gravity', 'horizontal_drag', 'solid_entities', 'dynamic_entities')

    def __init__(self, timestep_milliseconds: int, gravity: float, horizontal_drag: float, entities: List[Entity]):
        # FIXME It's always milliseconds in the interface, change the name
        self.timestep_milliseconds = timestep_milliseconds
        self.timestep_seconds = timestep_milliseconds / 1000
        self.time_accumulator = 0
        self.last_update_time = get_current_time()
        self.gravity = gravity
        self.horizontal_drag = horizontal_drag
        self.solid_entities = [e for e in entities if e.kind == EntityKind.SOLID]
        self.dynamic_entities = [e for e in entities if e.kind == EntityKind.DYNAMIC]

    def update(self) -> None:
        t = get_current_time()
        self.time_accumulator += t - self.last_update_time
        self.last_update_time = t
        while self.time_accumulator >= self.timestep_milliseconds:
            self.update_physics()
            self.time_accumulator -= self.timestep_milliseconds

    def update_physics(self) -> None:
        for entity in self.dynamic_entities:
            self.apply_gravity(entity)
            entity.velocity += entity.acceleration() * self.timestep_seconds
            entity.force -= self.horizontal_drag * entity.force.real
            self.solve_collisions(entity)
            entity.position += entity.velocity
            entity.velocity -= self.horizontal_drag * entity.velocity.real
            entity.physics_update()

    def apply_gravity(self, entity: Entity) -> None:
        entity.force += entity.mass * self.gravity * 1j

    def solve_collisions(self, entity: Entity) -> None:
        assert entity.kind == EntityKind.DYNAMIC
        for solid_entity in self.solid_entities:
            World.solve_collision(entity, solid_entity)

    @staticmethod
    def solve_collision(entity: Entity, solid_entity: Entity) -> None:
        assert entity.kind == EntityKind.DYNAMIC
        assert solid_entity.kind == EntityKind.SOLID

        if entity.velocity.real >= 0:
            if entity.velocity.imag >= 0:
                World.solve_vertical_collision(entity, Corner.LOWER_RIGHT, solid_entity.checkbox.left_line)
                World.solve_horizontal_collision(entity, Corner.LOWER_RIGHT, solid_entity.checkbox.top_line)
            if entity.velocity.imag <= 0:
                World.solve_vertical_collision(entity, Corner.UPPER_RIGHT, solid_entity.checkbox.left_line)
                World.solve_horizontal_collision(entity, Corner.UPPER_RIGHT, solid_entity.checkbox.bottom_line)
        if entity.velocity.real <= 0:
            if entity.velocity.imag >= 0:
                World.solve_vertical_collision(entity, Corner.LOWER_LEFT, solid_entity.checkbox.left_line)
                World.solve_horizontal_collision(entity, Corner.LOWER_LEFT, solid_entity.checkbox.top_line)
            if entity.velocity.imag <= 0:
                World.solve_vertical_collision(entity, Corner.UPPER_LEFT, solid_entity.checkbox.right_line)
                World.solve_horizontal_collision(entity, Corner.UPPER_LEFT, solid_entity.checkbox.bottom_line)

    # Horizontal collision should mean collision *on the horizontal axis*
    # Swap the names
    @staticmethod
    def solve_horizontal_collision(entity: Entity, corner: Corner, line: Line) -> None:
        if not line.intersects(Line(entity.position, entity.velocity)):
            return
        if corner is Corner.UPPER_LEFT or corner is Corner.UPPER_RIGHT:
            entity.checkbox.upper_imag = line.start.imag
        elif corner is Corner.LOWER_LEFT or corner is Corner.LOWER_RIGHT:
            entity.checkbox.lower_imag = line.start.imag
        entity.velocity = entity.velocity.real
        entity.force = entity.force.real

    @staticmethod
    def solve_vertical_collision(entity: Entity, corner: Corner, line: Line) -> None:
        if not line.intersects(Line(entity.position, entity.velocity)):
            return
        if corner is Corner.UPPER_LEFT or corner is Corner.LOWER_LEFT:
            entity.checkbox.left_real = line.start.real
        if corner is Corner.UPPER_RIGHT or corner is Corner.LOWER_RIGHT:
            entity.checkbox.right_real = line.start.real
        entity.velocity = entity.velocity.imag * 1j
        entity.force = entity.force.imag * 1j
