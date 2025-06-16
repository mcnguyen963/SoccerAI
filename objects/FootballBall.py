import math
import pygame
from .Collidable import Collidable
class FootballBall(Collidable):
    FRICTION = 0.995 # friction slows down the ball each update

    def __init__(self, x, y, radius=10, mass=100, colour=(255, 255, 255)):
        self.x = x
        self.y = y
        self.radius = radius
        self.mass = mass
        self.colour = colour

        self.vel_x = 0
        self.vel_y = 0

    def update(self, world, dt):
        self.update_position(dt)
        self.check_bouncing(world.field)
        self.update_speed(dt)
        self.handle_collisions(world.collidable_objects)

    def update_position(self,dt):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
    def check_bouncing(self,field):
        left = field.offset
        right = field.offset + field.length
        top = field.offset
        bottom = field.offset + field.width

        if self.x - self.radius < left:
            self.x = left + self.radius
            self.vel_x *= -1
        elif self.x + self.radius > right:
            self.x = right - self.radius
            self.vel_x *= -1

        if self.y - self.radius < top:
            self.y = top + self.radius
            self.vel_y *= -1
        elif self.y + self.radius > bottom:
            self.y = bottom - self.radius
            self.vel_y *= -1
    def update_speed(self, dt):
        self.vel_x *= self.FRICTION
        self.vel_y *= self.FRICTION

    def draw(self, surface):
        pygame.draw.circle(surface, self.colour, (int(self.x), int(self.y)), self.radius)
