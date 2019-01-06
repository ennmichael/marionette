from __future__ import annotations

from collections import OrderedDict
from typing import Iterable, Generic, TypeVar, Optional

from engine.graphics import Camera, SpritePlayer, Sprite
from engine.physics import PhysicalEntity
from engine.sdl import Flip, Destroyable, EventHandler, Keyboard
from engine.timer import Time
from engine.utils import Rectangle


class Actor(PhysicalEntity):
    __slots__ = 'sprite_player', 'flip'

    def __init__(
            self, sprite: Sprite, checkbox: Rectangle, flip: Flip = Flip.NONE, gravity_scale: float = 1) -> None:
        super().__init__(checkbox, gravity_scale)
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
    __slots__ = 'trigger'

    def __init__(self) -> None:
        self.trigger = False

    def enter(self, parent: T_Parent) -> None:
        pass

    def update(self, parent: T_Parent) -> None:
        pass

    def physics_update(self, parent: T_Parent) -> None:
        pass

    def exit(self, parent: T_Parent) -> None:
        pass


class StateGraph(Generic[T_Parent]):
    __slots__ = 'connections', 'any_state_connections'

    def __init__(
            self,
            connections: OrderedDict[State[T_Parent], Iterable[State[T_Parent]]],
            any_state_connections: Iterable[State[T_Parent]]) -> None:
        self.connections = connections
        self.any_state_connections = any_state_connections


class GenericStateMachine(Generic[T_Parent]):
    __slots__ = 'parent', 'current_state', 'default_state', 'state_graph'

    def __init__(self, parent: T_Parent, default_state: State[T_Parent], state_graph: StateGraph[T_Parent]) -> None:
        self.parent = parent
        self.current_state = default_state
        self.current_state.enter(self.parent)
        self.default_state = default_state
        self.state_graph = state_graph

    def update(self) -> None:
        if not self.execute_triggers():
            self.switch_state(self.default_state)
        self.current_state.update(self.parent)

    def physics_update(self) -> None:
        self.current_state.physics_update(self.parent)

    def execute_triggers(self) -> bool:
        return any(self.execute_trigger(state) for state in self.states)

    def execute_trigger(self, state: State[T_Parent]) -> bool:
        if not state.trigger:
            return False
        return self.switch_state(state)

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
    def states(self) -> Iterable[State[T_Parent]]:
        return self.state_graph.connections.keys()

    @property
    def reachable_states(self) -> Iterable[State[T_Parent]]:
        if self.current_state in self.state_graph.connections:
            yield from self.state_graph.connections[self.current_state]
        yield from self.state_graph.any_state_connections


class Game(Destroyable):
    __slots__ = 'frame_time', 'event_handler'

    def __init__(self, fps: int, event_handler: Optional[EventHandler] = None) -> None:
        self.frame_time = round(1000 / fps)
        self.event_handler = event_handler or EventHandler()

    def destroy(self) -> None:
        pass

    @property
    def keyboard(self) -> Keyboard:
        return self.event_handler.keyboard

    def main_loop(self) -> None:
        time = Time.now()
        while not self.event_handler.quit_requested:
            new_time = time.updated()
            if new_time.delta < self.frame_time:
                continue
            time = new_time
            self.frame_advance(time)
            print(1000 / time.delta)

    def frame_advance(self, time: Time) -> None:
        self.event_handler.update()
