from __future__ import annotations

from engine.game import Actor, GenericStateMachine, State, ANY_STATE
from engine.graphics import Sprite, Animation
from engine.sdl import Texture, Scancode, Flip, Keyboard
from engine.timer import Time
from engine.utils import Rectangle, Direction


# TODO Flow of time through the program is still inconsistent
# Sometimes time is received as a parameter, sometimes I call get_current_time
# Ideally I should only call get_current_time in one place


class Mario(Actor):
    class Idling(State['Mario']):
        def enter(self, mario: Mario) -> None:
            mario.switch_sprite(mario.sprites.idle)

    class Running(State['Mario']):
        def enter(self, mario: Mario) -> None:
            mario.switch_sprite(mario.sprites.running)

        def physics_update(self, mario: Mario) -> None:
            mario.update_real_speed()

    class Ducking(State['Mario']):
        def enter(self, mario: Mario) -> None:
            mario.switch_sprite(mario.sprites.ducking)

    class Jumping(State['Mario']):
        def enter(self, mario: Mario) -> None:
            mario.velocity = mario.velocity.real + mario.jump_velocity

    class MidAir(State['Mario']):
        def enter(self, mario: Mario) -> None:
            mario.switch_sprite(mario.sprites.mid_air)

        def physics_update(self, mario: Mario) -> None:
            mario.update_real_speed()

    class StateMachine(GenericStateMachine['Mario']):
        def __init__(self, mario: Mario) -> None:
            self.duck = False
            self.run = False
            self.jump = False
            self.idling = Mario.Idling()
            self.running = Mario.Running()
            self.ducking = Mario.Ducking()
            self.jumping = Mario.Jumping()
            self.mid_air = Mario.MidAir()
            self.mario = mario
            super().__init__(parent=self.mario, starting_state=self.idling, state_graph={
                self.idling: (self.running, self.ducking, self.jumping),
                self.running: (self.jumping, self.ducking),
                self.jumping: (self.mid_air,),
                self.mid_air: (self.jumping, self.running, self.ducking, self.idling),
                ANY_STATE: (self.idling, self.mid_air)
            })

        def update(self) -> None:
            super().update()

            if not self.mario.on_ground:
                self.switch_state(self.mid_air)
                return

            if self.duck:
                self.switch_state(self.ducking) or self.switch_state(self.idling)
            elif self.jump:
                self.switch_state(self.jumping) or self.switch_state(self.idling)
            elif self.run:
                self.switch_state(self.running) or self.switch_state(self.idling)
            else:
                self.switch_state(self.idling)

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

    def __init__(self, upper_left: complex, texture: Texture) -> None:
        self.sprites = Mario.Sprites(texture)
        super().__init__(sprite=self.sprites.idle, checkbox=Rectangle(upper_left, dimensions=16 + 32j))
        self.keyboard = Keyboard()
        self.state_machine = Mario.StateMachine(self)
        self.speed = 200.0
        self.jump_velocity = -200j
        self.direction = Direction.RIGHT

    def update(self, time: Time) -> None:
        print(self.state_machine.current_state)
        super().update(time)
        self.update_flip()
        self.state_machine.update()

    def physics_update(self) -> None:
        self.state_machine.duck = self.keyboard.key_down(Scancode.LEFT_CTRL)
        self.state_machine.jump = self.keyboard.key_down(Scancode.SPACE)

        if self.keyboard.key_down(Scancode.RIGHT):
            self.direction = Direction.RIGHT
            self.state_machine.run = True
        elif self.keyboard.key_down(Scancode.LEFT):
            self.direction = Direction.LEFT
            self.state_machine.run = True
        else:
            self.direction = Direction.NONE
            self.state_machine.run = False

        self.state_machine.physics_update()

    def update_flip(self) -> None:
        if self.direction == Direction.LEFT:
            self.flip = Flip.HORIZONTAL
        elif self.direction == Direction.RIGHT:
            self.flip = Flip.NONE

    def update_real_speed(self) -> None:
        self.velocity = float(self.direction) * self.speed + self.velocity.imag * 1j
