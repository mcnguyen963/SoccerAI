import math
import pygame
from .Collidable import Collidable
class FootballBall(Collidable):
    FRICTION = 0.993 # friction slows down the ball each update
    BOUNCING_FACTOR_FIELD= 0.9
    BOUNCING_FACTOR_GOAL = 0.5
    def __init__(self, x, y, radius=10, mass=100, colour=(253, 253, 253),window_scale = 1):
        self.starting_x = x
        self.starting_y = y
        self.x = x
        self.y = y
        self.mass = mass
        self.colour = colour
        self.window_scale = window_scale
        self.vel_x = 0
        self.vel_y = 0
        self.radius = radius * window_scale


    def update(self, world, dt):
        self.update_position(dt)
        field = world.field
        margin = self.radius + 5  # small margin buffer for bounce detection
        self.check_bouncing(field,world)
        self.update_speed(dt)
        self.handle_collisions(world.collidable_objects)

    def update_position(self,dt):
        self.x += self.vel_x * dt*self.window_scale
        self.y += self.vel_y * dt*self.window_scale
    def check_bouncing(self,field,world):
        left = field.offset
        right = field.offset + field.length
        top = field.offset
        bottom = field.offset + field.width

        if self.x - self.radius < left:
            self.x = left + self.radius
            self.vel_x *= -1*self.BOUNCING_FACTOR_FIELD
            self.check_goal(world, is_left= True)

        elif self.x + self.radius > right:
            self.x = right - self.radius
            self.vel_x *= -1*self.BOUNCING_FACTOR_FIELD
            self.check_goal(world)

        if self.y - self.radius < top:
            self.y = top + self.radius
            self.vel_y *= -1*self.BOUNCING_FACTOR_FIELD
        elif self.y + self.radius > bottom:
            self.y = bottom - self.radius
            self.vel_y *= -1*self.BOUNCING_FACTOR_FIELD

    def update_speed(self, dt):
        self.vel_x *= self.FRICTION
        self.vel_y *= self.FRICTION

    def draw(self, surface):
        pygame.draw.circle(surface, self.colour, (int(self.x), int(self.y)), self.radius)

    def check_goal(self, world, is_left= False):
        field = world.field

        # Left goal check
        goal_y_start = field.left_goal_pos[1]
        goal_y_end = field.left_goal_pos[2]

        for team in world.teams:
            if team.is_on_left_side == False:
                right_team = team
            else:
                left_team = team

        if goal_y_start <= self.y <= goal_y_end:
            if is_left:
                right_team.score += 1
            else:
                left_team.score += 1
            self.reset_ball_position()

    def reset_ball_position(self):
        self.x = self.starting_x
        self.y = self.starting_y
        self.vel_x =0
        self.vel_y =0


