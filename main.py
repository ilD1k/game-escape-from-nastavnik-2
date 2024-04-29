from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import subprocess
from ursina.prefabs.health_bar import HealthBar

from ursina.shaders import *


#Entity.default_shader = camera_vertical_blur_shader


subprocess.call("key.mp3", shell=True)
editor_camera = EditorCamera(enabled=False, ignore_paused=True)

app = Ursina()
Sky()
ground = Entity(
    model="plane",
    texture="assets/esss.jfif",
    collider="mesh",
    scale=(100, 1, 100))

player = FirstPersonController(position=(0, 2, -5), speed=12)


gun = Entity(
    model="sphere",
    texture="assets/akk47.png",
    parent=camera,
    position=(.5,-.25,.25),
    scale=(0.5),
    origin_z=-.5,
    on_cooldown=False
)

gun.muzzle_flash = Entity(parent=gun, z=1, world_scale=.5, model='quad', color=color.yellow, enabled=False)

shootables_parent = Entity()
mouse.traverse_target = shootables_parent



wall1 = Entity(
    model="cube",
    texture="assets/esss.jfif",
    collider="cube",
    scale=(100, 10, 5),
    position=(0, 5, 50))

wall2 = duplicate(wall1, z=-50)
wall3 = duplicate(wall1, rotation_y=90, x=-50, z=0)
wall4 = duplicate(wall3, x=50)


def update():
    if held_keys['left mouse']:
            shoot()
def shoot():
    if not gun.on_cooldown:
        gun.on_cooldown = True
        gun.muzzle_flash.enabled=True
        from ursina.prefabs.ursfx import ursfx
        ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise', pitch=random.uniform(-13,-12), pitch_change=-12, speed=3.0)
        invoke(gun.muzzle_flash.disable, delay=.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=.15)
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.hp -= 10
            mouse.hovered_entity.blink(color.red)



class Enemy(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=shootables_parent, model='cube', scale_y=2, origin_y=-.5, texture="assets/python.png", collider='box', **kwargs)
        self.health_bar = Entity(parent=self, y=1.2, model='cube', color=color.red, world_scale=(1.5,.1,.1))
        self.max_hp = 100
        self.hp = self.max_hp

    def update(self):
        dist = distance_xz(player.position, self.position)
        if dist > 40:
            return

        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)


        self.look_at_2d(player.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0,1,0), self.forward, 30, ignore=(self,))
        if hit_info.entity == player:
            if dist > 2:
                self.position += self.forward * time.dt * 5

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value#
        if value <= 0:
            destroy(self)
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1

# Enemy()
enemies = [Enemy(x=x*4) for x in range(10)]


def pause_input(key):
    if key == 'tab':   # свободная камера ок ????
        editor_camera.enabled = not editor_camera.enabled

        player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        gun.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position

        application.paused = editor_camera.enabled

pause_handler = Entity(ignore_paused=True, input=pause_input)


app.run()
