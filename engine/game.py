from __future__ import annotations

from typing import Dict, Iterable, Generic, TypeVar, Union

from engine.graphics import Camera, SpritePlayer, Sprite
from engine.physics import PhysicalEntity, EntityKind
from engine.sdl import Flip
from engine.timer import Time
from engine.utils import Rectangle


class Actor(PhysicalEntity):
    __slots__ = 'sprite_player', 'flip'

    def __init__(
            self, sprite: Sprite, checkbox: Rectangle, flip: Flip = Flip.NONE,
            kind: EntityKind = EntityKind.DYNAMIC, gravity_scale: float = 1) -> None:
        super().__init__(checkbox, kind, gravity_scale)
        self.sprite_player = SpritePlayer(sprite)
        self.flip = flip

    @property
    def sprite(self) -> Sprite:
        return self.sprite_player.sprite

    def switch_sprite(self, new_sprite: Sprite) -> None:
        self.sprite_player = SpritePlayer(new_sprite)

    def update(self, time: Time) -> None:
        self.sprite_player.update(time)

    def render(self, camera: Camera) -> None:
        self.sprite.render(camera, destination=self.checkbox, flip=self.flip)


T_Parent = TypeVar('T_Parent')


class State(Generic[T_Parent]):
    __slots__ = ()

    def enter(self, parent: T_Parent) -> None:
        pass

    def update(self, parent: T_Parent) -> None:
        pass

    def physics_update(self, parent: T_Parent) -> None:
        pass

    def exit(self, parent: T_Parent) -> None:
        pass


class AnyState:
    pass


ANY_STATE = AnyState()

StateGraph = Dict[Union[AnyState, State[T_Parent]], Iterable[State[T_Parent]]]


class GenericStateMachine(Generic[T_Parent]):
    __slots__ = 'parent', 'current_state', 'state_graph'

    def __init__(self, parent: T_Parent, starting_state: State[T_Parent], state_graph: StateGraph[T_Parent]) -> None:
        self.parent = parent
        self.current_state = starting_state
        self.current_state.enter(self.parent)
        self.state_graph = state_graph

    def update(self) -> None:
        self.current_state.update(self.parent)

    def physics_update(self) -> None:
        self.current_state.physics_update(self.parent)

    def switch_state(self, new_state: State[T_Parent]) -> bool:
        if new_state is self.current_state:
            return True

        if new_state not in self.reachable_states:
            return False

        self.current_state.exit(self.parent)
        self.current_state = new_state
        self.current_state.enter(self.parent)

        return True

    @property
    def reachable_states(self) -> Iterable[State[T_Parent]]:
        if self.current_state in self.state_graph:
            yield from self.state_graph[self.current_state]
        if ANY_STATE in self.state_graph:
            yield from (s for s in self.state_graph[ANY_STATE] if s is not self.current_state)
