import math
import pygame

class FootballBall:
    FRICTION = 0.9999 # friction slows down the ball each update

    def __init__(self, x, y, radius=10, mass=1, colour=(255, 255, 255)):
        self.x = x
        self.y = y
        self.radius = radius
        self.mass = mass
        self.colour = colour

        self.vel_x = 0
        self.vel_y = 0

    def update(self, dt):
        # Move ball by current velocity
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt

        # Apply friction to slow ball down
        self.vel_x *= self.FRICTION
        self.vel_y *= self.FRICTION


    def draw(self, surface):
        pygame.draw.circle(surface, self.colour, (int(self.x), int(self.y)), self.radius)
