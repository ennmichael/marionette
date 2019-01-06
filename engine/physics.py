from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Any

from math import isclose

from engine.timer import Time
from engine.utils import Rectangle, Line, Corner


class PhysicalEntity:
    __slots__ = 'checkbox', 'acceleration', 'velocity', 'gravity_scale', 'on_ground'

    def __init__(self, checkbox: Rectangle, gravity_scale: float = 1) -> None:
        self.checkbox = checkbox
        self.acceleration = 0 + 0j
        self.velocity = 0 + 0j
        self.gravity_scale = gravity_scale
        self.on_ground = False

    def update(self, time: Time) -> None:
        pass

    def physics_update(self) -> None:
        pass

    def hit_ground(self, ground_imag: float) -> None:
        self.checkbox.lower_imag = ground_imag
        self.velocity = self.velocity.real
        self.acceleration = self.acceleration.real

    def hit_roof(self, roof_imag: float) -> None:
        self.checkbox.upper_imag = roof_imag
        self.velocity = self.velocity.real
        self.acceleration = self.acceleration.real

    def hit_left_wall(self, wall_real: float) -> None:
        self.checkbox.left_real = wall_real
        self.velocity = self.velocity.imag * 1j
        self.acceleration = self.acceleration.imag * 1j

    def hit_right_wall(self, wall_real: float) -> None:
        self.checkbox.right_real = wall_real
        self.velocity = self.velocity.imag * 1j
        self.acceleration = self.acceleration.imag * 1j


class TerrainElement(ABC):
    __slots__ = ()

    @abstractmethod
    def solve_collision(self, entity: PhysicalEntity, timestep: float) -> None:
        pass

    def is_ground(self, entity: PhysicalEntity) -> bool:
        return False


# Perhaps in the future I should delete this class
class Block(TerrainElement):
    __slots__ = 'checkbox'

    def __init__(self, upper_left: complex, dimensions: complex) -> None:
        self.checkbox = Rectangle(upper_left, dimensions)

    def solve_collision(self, entity: PhysicalEntity, timestep: float) -> None:
        if entity.velocity.real >= 0:
            if entity.velocity.imag >= 0:
                solve_imag_axes_collision(entity, Corner.LOWER_RIGHT, self.checkbox.top_line, timestep)
                solve_imag_axes_collision(entity, Corner.LOWER_LEFT, self.checkbox.top_line, timestep)
                solve_real_axis_collision(entity, Corner.LOWER_RIGHT, self.checkbox.left_line, timestep)
            if entity.velocity.imag <= 0:
                solve_imag_axes_collision(entity, Corner.UPPER_RIGHT, self.checkbox.bottom_line, timestep)
                solve_real_axis_collision(entity, Corner.UPPER_RIGHT, self.checkbox.left_line, timestep)
                solve_real_axis_collision(entity, Corner.LOWER_RIGHT, self.checkbox.left_line, timestep)
        if entity.velocity.real <= 0:
            if entity.velocity.imag >= 0:
                solve_imag_axes_collision(entity, Corner.LOWER_LEFT, self.checkbox.top_line, timestep)
                solve_imag_axes_collision(entity, Corner.LOWER_RIGHT, self.checkbox.top_line, timestep)
                solve_real_axis_collision(entity, Corner.LOWER_LEFT, self.checkbox.right_line, timestep)
            if entity.velocity.imag <= 0:
                solve_imag_axes_collision(entity, Corner.UPPER_LEFT, self.checkbox.bottom_line, timestep)
                solve_real_axis_collision(entity, Corner.UPPER_LEFT, self.checkbox.right_line, timestep)
                solve_real_axis_collision(entity, Corner.LOWER_LEFT, self.checkbox.right_line, timestep)

    def is_ground(self, entity: PhysicalEntity) -> bool:
        return (self.checkbox.overlaps_on_real_axis(entity.checkbox) and
                isclose(self.checkbox.upper_imag, entity.checkbox.lower_imag, abs_tol=1.0001))


class Platform(TerrainElement):
    __slots__ = 'line'

    def __init__(self, origin: complex, width: float) -> None:
        self.line = Line(origin, offset=width)

    def solve_collision(self, entity: PhysicalEntity, timestep: float) -> None:
        assert self.line.is_horizontal

        if entity.velocity.imag <= 0:
            return

        solve_imag_axes_collision(entity, Corner.LOWER_LEFT, self.line, timestep)
        solve_imag_axes_collision(entity, Corner.LOWER_RIGHT, self.line, timestep)

    def is_ground(self, entity: PhysicalEntity) -> bool:
        assert self.line.is_horizontal

        return (self.line.overlaps_on_real_axis(entity.checkbox.bottom_line) and
                isclose(self.line.origin.imag, entity.checkbox.lower_imag, abs_tol=1.0001))


class Wall(TerrainElement):
    __slots__ = 'line'

    def __init__(self, origin: complex, height: float) -> None:
        self.line = Line(origin, offset=height * 1j)

    def solve_collision(self, entity: PhysicalEntity, timestep: float) -> None:
        assert self.line.is_vertical

        if entity.velocity.real > 0:
            solve_real_axis_collision(entity, Corner.LOWER_RIGHT, self.line, timestep)
            solve_real_axis_collision(entity, Corner.UPPER_RIGHT, self.line, timestep)
        elif entity.velocity.real < 0:
            solve_real_axis_collision(entity, Corner.LOWER_LEFT, self.line, timestep)
            solve_real_axis_collision(entity, Corner.UPPER_LEFT, self.line, timestep)


class Roof(TerrainElement):
    __slots__ = 'line'

    def __init__(self, origin: complex, width: float) -> None:
        self.line = Line(origin, offset=width)

    def solve_collision(self, entity: PhysicalEntity, timestep: float) -> None:
        assert self.line.is_horizontal

        if entity.velocity.imag >= 0:
            return

        solve_imag_axes_collision(entity, Corner.UPPER_LEFT, self.line, timestep)
        solve_imag_axes_collision(entity, Corner.UPPER_RIGHT, self.line, timestep)


def solve_imag_axes_collision(entity: PhysicalEntity, corner: Corner, line: Line, timestep: float) -> None:
    assert line.is_horizontal

    if not line.intersects(Line(entity.checkbox.get_point(corner), entity.velocity * timestep)):
        return

    if corner is Corner.UPPER_LEFT or corner is Corner.UPPER_RIGHT:
        entity.hit_roof(line.origin.imag)
    elif corner is Corner.LOWER_LEFT or corner is Corner.LOWER_RIGHT:
        entity.hit_ground(line.origin.imag)
    else:
        assert False


def solve_real_axis_collision(entity: PhysicalEntity, corner: Corner, line: Line, timestep: float) -> None:
    assert line.is_vertical

    if not line.intersects(Line(entity.checkbox.get_point(corner), entity.velocity * timestep)):
        return

    if corner is Corner.UPPER_LEFT or corner is Corner.LOWER_LEFT:
        entity.hit_left_wall(line.origin.real)
    elif corner is Corner.UPPER_RIGHT or corner is Corner.LOWER_RIGHT:
        entity.hit_right_wall(line.origin.real)
    else:
        assert False


class Integrator:
    __slots__ = (
        'timestep_milliseconds', 'timestep_seconds', 'time_accumulator',
        'gravity', 'horizontal_drag', 'entities', 'terrain')

    def __init__(
            self, timestep: int, gravity: float, horizontal_drag: float,
            entities: Iterable[PhysicalEntity], terrain: Iterable[TerrainElement]):
        self.timestep_milliseconds = timestep
        self.timestep_seconds = timestep / 1000
        self.time_accumulator = 0
        self.gravity = gravity
        self.horizontal_drag = horizontal_drag
        self.entities = entities
        self.terrain = terrain

    def update(self, time: Time) -> None:
        self.time_accumulator += time.delta
        for entity in self.entities:
            entity.update(time)
        while self.time_accumulator >= self.timestep_milliseconds:
            self.update_physics()
            self.time_accumulator -= self.timestep_milliseconds

    def update_physics(self) -> None:
        for entity in self.entities:
            self.apply_gravity(entity)
            entity.velocity += entity.acceleration * self.timestep_seconds
            entity.velocity -= entity.velocity.real * self.horizontal_drag
            self.solve_collisions(entity)
            entity.checkbox.upper_left += entity.velocity * self.timestep_seconds
            self.update_on_ground(entity)
            entity.physics_update()

    def apply_gravity(self, entity: PhysicalEntity) -> None:
        if entity.acceleration.imag <= 0:
            entity.acceleration = entity.acceleration.real + self.gravity * 1j

    def solve_collisions(self, entity: PhysicalEntity) -> None:
        for terrain_element in self.terrain:
            terrain_element.solve_collision(entity, self.timestep_seconds)

    def update_on_ground(self, entity: PhysicalEntity) -> None:
        if entity.velocity.imag < 0:
            entity.on_ground = False
            return
        entity.on_ground = any(terrain_element.is_ground(entity) for terrain_element in self.terrain)
