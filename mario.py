from __future__ import annotations

from collections import OrderedDict

from engine.game import Actor, GenericStateMachine, State, StateGraph
from engine.graphics import Sprite, Animation
from engine.sdl import Texture, Scancode, Flip, Keyboard
from engine.timer import Time
from engine.utils import Rectangle, Direction


class Mario(Actor):
    class Idling(State['Mario']):
        def enter(self, mario: Mario) -> None:
            mario.switch_sprite(mario.sprites.idle)

    class Running(State['Mario']):
        def enter(self, mario: Mario) -> None:
            mario.switch_sprite(mario.sprites.running)

        def physics_update(self, timestep: float, mario: Mario) -> None:
            mario.update_real_speed()

    class Ducking(State['Mario']):
        def enter(self, mario: Mario) -> None:
            mario.switch_sprite(mario.sprites.ducking)

    class Stunned(State['Mario']):
        def __init__(self) -> None:
            super().__init__()
            self.direction = Direction.NONE
            self.remaining_duration = 0.0

        def enter(self, mario: Mario) -> None:
            mario.switch_sprite(mario.sprites.ducking)
            self.direction = mario.direction
            self.remaining_duration = mario.stun_duration

        def update(self, time: Time, mario: Mario) -> None:
            mario.direction = self.direction
            self.remaining_duration -= time.delta
            if self.remaining_duration <= 0:
                self.trigger = False

    class Jumping(State['Mario']):
        def enter(self, mario: Mario) -> None:
            mario.velocity = mario.velocity.real + mario.jump_velocity

    class MidAir(State['Mario']):
        def enter(self, mario: Mario) -> None:
            mario.switch_sprite(mario.sprites.mid_air)

        def physics_update(self, timestep: float, mario: Mario) -> None:
            mario.update_real_speed()

    class StateMachine(GenericStateMachine['Mario']):
        def __init__(self, mario: Mario) -> None:
            self.idling = Mario.Idling()
            self.running = Mario.Running()
            self.ducking = Mario.Ducking()
            self.stunned = Mario.Stunned()
            self.jumping = Mario.Jumping()
            self.mid_air = Mario.MidAir()
            self.mario = mario
            super().__init__(parent=self.mario, default_state=self.idling, state_graph=StateGraph(
                connections=OrderedDict([
                    (self.stunned, ()),
                    (self.jumping, (self.mid_air,)),
                    (self.idling, (self.running, self.ducking, self.jumping)),
                    (self.ducking, ()),
                    (self.mid_air, (self.stunned, self.jumping, self.idling)),
                    (self.running, (self.jumping, self.ducking)),
                ]),
                any_state_connections=(self.idling, self.mid_air)))

        def update(self, time: Time) -> None:
            print(self.current_state)
            super().update(time)

        def physics_update(self, timestep: float) -> None:
            super().physics_update(timestep)
            self.mid_air.trigger = not self.mario.on_ground

    class Sprites:
        def __init__(self, texture: Texture) -> None:
            self.ducking = Sprite(texture, Animation(
                starting_frame=Rectangle(upper_left=0, dimensions=16 + 32j),
                frame_count=2, frame_delay=100, loop=True))
            self.idle = Sprite(texture, Animation(
                starting_frame=Rectangle(upper_left=32, dimensions=16 + 32j),
                frame_count=2, frame_delay=100, loop=True))
            self.running = Sprite(texture, Animation(
                starting_frame=Rectangle(upper_left=80, dimensions=16 + 32j),
                frame_count=3, frame_delay=100, loop=True))
            self.mid_air = Sprite(texture, Animation(
                starting_frame=Rectangle(upper_left=64, dimensions=16 + 32j),
                frame_count=1, frame_delay=0, loop=True))

    def __init__(self, keyboard: Keyboard, upper_left: complex, texture: Texture) -> None:
        self.sprites = Mario.Sprites(texture)
        super().__init__(sprite=self.sprites.idle, checkbox=Rectangle(upper_left, dimensions=16 + 32j))
        self.speed = 200.0
        self.jump_velocity = -200j
        self.direction = Direction.NONE
        self.stun_duration = 1000.0
        self.stun_velocity = 320.0
        self.keyboard = keyboard
        self.state_machine = Mario.StateMachine(self)

    def hit_ground(self, ground_imag: float) -> None:
        if self.velocity.imag >= self.stun_velocity:
            self.state_machine.stunned.trigger = True
        super().hit_ground(ground_imag)

    def update(self, time: Time) -> None:
        print(self.velocity.imag)
        super().update(time)
        self.state_machine.update(time)
        self.update_flip()

    def physics_update(self, timestep: float) -> None:
        super().physics_update(timestep)
        self.handle_keyboard()
        self.state_machine.physics_update(timestep)

    def handle_keyboard(self) -> None:
        self.state_machine.ducking.trigger = self.keyboard.key_down(Scancode.LEFT_CTRL)
        self.state_machine.jumping.trigger = self.keyboard.key_down(Scancode.SPACE) and self.on_ground

        if self.keyboard.key_down(Scancode.RIGHT):
            self.direction = Direction.RIGHT
            self.state_machine.running.trigger = True
        elif self.keyboard.key_down(Scancode.LEFT):
            self.direction = Direction.LEFT
            self.state_machine.running.trigger = True
        else:
            self.direction = Direction.NONE
            self.state_machine.running.trigger = False

    def update_flip(self) -> None:
        if self.direction == Direction.LEFT:
            self.flip = Flip.HORIZONTAL
        elif self.direction == Direction.RIGHT:
            self.flip = Flip.NONE

    def update_real_speed(self) -> None:
        self.velocity = float(self.direction) * self.speed + self.velocity.imag * 1j
