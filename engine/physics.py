from __future__ import annotations

import enum
from typing import List, Iterable

from engine.sdl import get_current_time
from engine.utils import Rectangle, Line, Corner


@enum.unique
class EntityKind(enum.Enum):
    DYNAMIC = enum.auto()
    STATIC = enum.auto()
    SOLID = enum.auto()


class Entity:
    __slots__ = 'checkbox', 'mass', 'force', 'velocity', 'kind', 'gravity_scale'

    def __init__(
            self, position: complex, dimensions: complex, mass: float,
            kind: EntityKind = EntityKind.DYNAMIC, gravity_scale: float = 1) -> None:
        self.checkbox = Rectangle(upper_left=position, dimensions=dimensions)
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
    def position(self) -> complex:
        return self.checkbox.upper_left

    @position.setter
    def position(self, value: complex) -> None:
        self.checkbox.upper_left = value

    @property
    def dimensions(self) -> complex:
        return self.checkbox.dimensions

    @dimensions.setter
    def dimensions(self, value: complex) -> None:
        self.checkbox.dimensions = value


class TerrainBox(Entity):
    def __init__(self, position: complex, dimensions: complex) -> None:
        super().__init__(position, dimensions, mass=1, kind=EntityKind.SOLID, gravity_scale=0)


Entities = List[Entity]


class World:
    __slots__ = (
        'timestep_milliseconds', 'timestep_seconds', 'time_accumulator', 'last_update_time',
        'gravity', 'horizontal_drag', 'dynamic_entities', 'solid_entities', 'static_entities')

    def __init__(self, timestep: int, gravity: float, horizontal_drag: float, entities: List[Entity]):
        self.timestep_milliseconds = timestep
        self.timestep_seconds = timestep / 1000
        self.time_accumulator = 0
        self.last_update_time = get_current_time()
        self.gravity = gravity
        self.horizontal_drag = horizontal_drag
        # FIXME This is inefficient, taking three passes through the entities when only one would be enough
        self.dynamic_entities = [e for e in entities if e.kind == EntityKind.DYNAMIC]
        self.solid_entities = [e for e in entities if e.kind == EntityKind.SOLID]
        self.static_entities = [e for e in entities if e.kind == EntityKind.STATIC]

    @property
    def entities(self) -> Iterable[Entity]:
        yield from self.dynamic_entities
        yield from self.solid_entities
        yield from self.static_entities

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
            entity.velocity -= self.horizontal_drag * entity.velocity.real
            entity.force -= self.horizontal_drag * entity.force.real
            self.solve_collisions(entity)
            entity.position += entity.velocity
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
            if entity.velocity.imag > 0:
                World.solve_imag_axes_collision(entity, Corner.LOWER_RIGHT, solid_entity.checkbox.top_line)
                World.solve_imag_axes_collision(entity, Corner.LOWER_LEFT, solid_entity.checkbox.top_line)
                World.solve_real_axis_collision(entity, Corner.LOWER_RIGHT, solid_entity.checkbox.left_line)
            else:
                World.solve_imag_axes_collision(entity, Corner.UPPER_RIGHT, solid_entity.checkbox.bottom_line)
                World.solve_real_axis_collision(entity, Corner.UPPER_RIGHT, solid_entity.checkbox.left_line)
                World.solve_real_axis_collision(entity, Corner.LOWER_RIGHT, solid_entity.checkbox.left_line)
        else:
            if entity.velocity.imag > 0:
                World.solve_imag_axes_collision(entity, Corner.LOWER_LEFT, solid_entity.checkbox.top_line)
                World.solve_imag_axes_collision(entity, Corner.LOWER_RIGHT, solid_entity.checkbox.top_line)
                World.solve_real_axis_collision(entity, Corner.LOWER_LEFT, solid_entity.checkbox.right_line)
            else:
                World.solve_imag_axes_collision(entity, Corner.UPPER_LEFT, solid_entity.checkbox.bottom_line)
                World.solve_real_axis_collision(entity, Corner.UPPER_LEFT, solid_entity.checkbox.right_line)
                World.solve_real_axis_collision(entity, Corner.LOWER_LEFT, solid_entity.checkbox.right_line)

    @staticmethod
    def solve_imag_axes_collision(entity: Entity, corner: Corner, line: Line) -> None:
        assert line.is_horizontal()

        if not line.intersects(Line(entity.checkbox.get_point(corner), entity.velocity)):
            return
        if corner is Corner.UPPER_LEFT or corner is Corner.UPPER_RIGHT:
            entity.checkbox.upper_imag = line.start.imag
        elif corner is Corner.LOWER_LEFT or corner is Corner.LOWER_RIGHT:
            entity.checkbox.lower_imag = line.start.imag
        entity.velocity = entity.velocity.real
        entity.force = entity.force.real

    @staticmethod
    def solve_real_axis_collision(entity: Entity, corner: Corner, line: Line) -> None:
        assert line.is_vertical()

        if not line.intersects(Line(entity.checkbox.get_point(corner), entity.velocity)):
            return
        if corner is Corner.UPPER_LEFT or corner is Corner.LOWER_LEFT:
            entity.checkbox.left_real = line.start.real
        if corner is Corner.UPPER_RIGHT or corner is Corner.LOWER_RIGHT:
            entity.checkbox.right_real = line.start.real
        entity.velocity = entity.velocity.imag * 1j
        entity.force = entity.force.imag * 1j
