import pygame
import sys
import math
from .Collidable import Collidable
import enum


class FootballPLayer(Collidable):
    EXHAUST_PENALTY_FACTOR = 0.5
    BASE_STAMINA_REDUCE_RUNNING = 6
    BASE_STAMINA_REDUCE_WALKING = 5
    BASE_STAMINA_RECOVER = 4
    STAMINA_PENALTY_VALUE = 0 #player run speed and acceleration will reduce if under this point
    STAMINA_LOWEST_VALUE = -50 #Player won't be able to move after this
    BASE_SPEED_REDUCE_RATE = 0.95# friction cause player to stop if no control is given
    # how big player are
    STOPPING_SPEED = 0.05 # if player's speed below this part they will be stop

    def __init__(self, name, x, y, team, acceleration, run_speed, walk_speed, strength, stamina, dex, mass = 60,is_bot=True,radius =20,window_scale = 1):
        # value that player can change
        self.name = name
        self.is_bot = is_bot
        self.x = x
        self.y = y
        self.team = team
        self.window_scale = window_scale

        self.acceleration = acceleration # determent how fast the player can change speed or direction
        self.walk_speed = walk_speed # determent normal run speed
        self.run_speed = run_speed # determent the max speed player
        self.strength = strength # determent the kick speed

        self.MAX_STAMINA = stamina
        self.stamina = stamina
        self.dex = dex # this will determent
        self.mass = mass
        self.radius = radius*window_scale
        # innit value
        self.vel_x = 0
        self.vel_y = 0
        self.is_running = False
        self.facing_direction = (1,1)
        self.is_exhausted = False


    def apply_exhaustion_penalty(self, stats):
        if self.stamina < self.STAMINA_LOWEST_VALUE:
            self.stamina = self.STAMINA_LOWEST_VALUE
            return 0
        if self.stamina < self.STAMINA_PENALTY_VALUE:
            return stats * self.EXHAUST_PENALTY_FACTOR
        return stats

    def update(self,world, dt, dx, dy): #dx=-1 left, dý = down

        self.update_stamina(dt,dx,dy)
        self.update_speed(dt,dx,dy)
        self.move_to(dt)
        self.snap_to_field(world)
        self.handle_collisions(world.collidable_objects)
        self.try_kick_ball(world.balls)


    def snap_to_field(self,world):
        field = world.field

        self.x = max(self.radius,
                     min(2 * field.offset + field.length - self.radius, self.x))

        self.y = max(self.radius,
                     min(field.offset * 2 + field.width - self.radius, self.y))

    def update_speed(self, dt, dx, dy):
        self.vel_x *= self.BASE_SPEED_REDUCE_RATE

        self.vel_y *= self.BASE_SPEED_REDUCE_RATE

        # Normalize direction to prevent faster diagonal acceleration
        if (dx != 0 or dy != 0) and not self.is_exhausted:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length
            acc = self.apply_exhaustion_penalty(self.acceleration) * (2 if self.is_running else 1)

            ax = acc * dx * dt * 100
            ay = acc * dy * dt * 100

            # Clamp acceleration magnitude
            acc_magnitude = math.hypot(ax, ay)
            max_acc = self.apply_exhaustion_penalty(self.acceleration) * dt * 100
            if acc_magnitude > max_acc:
                scale = max_acc / acc_magnitude
                ax *= scale
                ay *= scale

            self.vel_x += ax
            self.vel_y += ay

        # Compute resulting speed
        speed = math.hypot(self.vel_x, self.vel_y)
        max_speed = self.apply_exhaustion_penalty((self.run_speed if self.is_running else self.walk_speed))

        # Clamp speed if it exceeds max
        if speed > max_speed:
            scale = max_speed / speed
            self.vel_x *= scale
            self.vel_y *= scale
        if abs(self.vel_x) < 0.1: self.vel_x = 0
        if abs(self.vel_y) < 0.1: self.vel_y = 0
        if self.vel_x != 0 or self.vel_y != 0:
            self.facing_direction = (self.vel_x, self.vel_y)


    def update_stamina(self,dt,dx,dy):
        if self.stamina >0:
            self.is_exhausted = False
        if self.stamina <=self.STAMINA_LOWEST_VALUE:
            self.is_exhausted = True

        if (dx == 0 and dy == 0) or self.is_exhausted:
            if self.stamina < self.MAX_STAMINA - self.BASE_STAMINA_RECOVER * dt:
                self.stamina += self.BASE_STAMINA_RECOVER * dt
        elif self.is_running:
            self.stamina -= self.BASE_STAMINA_REDUCE_RUNNING * dt
        else:
            self.stamina -= self.BASE_STAMINA_REDUCE_WALKING * dt

    def move_to(self, dt):
        # print(abs(self.vel_x*self.window_scale)*dt,self.vel_x*self.window_scale)
        self.x += self.vel_x * dt*self.window_scale
        self.y += self.vel_y * dt*self.window_scale


    def try_kick_ball(self, balls):
        for ball in balls:
            dx = ball.x - self.x
            dy = ball.y - self.y
            dist = math.hypot(dx, dy)

            if dist > self.radius + ball.radius:
                return  # Too far to kick

                # Player velocity magnitude (speed)
            speed = math.hypot(self.vel_x, self.vel_y)
            if speed == 0:
                return  # Player not moving, no kick

            # Normalize facing direction
            fx, fy = self.facing_direction
            facing_length = math.hypot(fx, fy)
            if facing_length == 0:
                return
            fx /= facing_length
            fy /= facing_length

            # Normalize vector from player to ball
            ball_dir_x = dx / dist
            ball_dir_y = dy / dist

            # Calculate angle between facing direction and ball direction using dot product
            dot = fx * ball_dir_x + fy * ball_dir_y
            # Clamp dot product between -1 and 1 to avoid math domain error with acos
            dot = max(min(dot, 1.0), -1.0)

            # Angle in radians
            angle = math.acos(dot)

            # 60 degree cone means 30 degrees on each side of facing direction
            # So accept if angle <= 30 degrees in radians
            max_angle_rad = math.radians(30)

            if angle > max_angle_rad:
                return  # Ball not in front cone

            # If all checks pass, kick the ball
            kick_speed = self.strength * speed
            ball.vel_x = ball_dir_x * kick_speed
            ball.vel_y = ball_dir_y * kick_speed

    def draw(self, surface):
        pygame.draw.circle(surface, self.team.colour, (int(self.x), int(self.y)), self.radius)
        line_length = 30*self.window_scale
        last_direction_x, last_direction_y = self.facing_direction
        end_x = self.x + last_direction_x * line_length/300
        end_y = self.y + last_direction_y * line_length/300

        pygame.draw.line(surface, (255, 255, 255), (int(self.x), int(self.y)), (int(end_x), int(end_y)), 2)
