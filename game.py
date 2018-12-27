from engine.graphics import Animator, Camera
from engine.physics import PhysicalEntity, EntityKind
from engine.utils import Rectangle


class Actor(PhysicalEntity):
    __slots__ = 'animator'

    def __init__(
            self, animator: Animator, checkbox: Rectangle,
            kind: EntityKind = EntityKind.DYNAMIC, gravity_scale: float = 1) -> None:
        super().__init__(checkbox, kind, gravity_scale)
        self.animator = animator

    def render(self, camera: Camera) -> None:
        self.animator.render_current_sprite(camera, destination=self.checkbox)
