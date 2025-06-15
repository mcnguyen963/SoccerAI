import pygame
import sys
import math

class FootballPLayer:
    EXHAUST_PENALTY_FACTOR = 0.5
    BASE_STAMINA = 100
    BASE_STAMINA_REDUCE_RUNNING = 10
    BASE_STAMINA_REDUCE_WALKING = 4
    BASE_STAMINA_RECOVER = 6
    BASE_STAMINA_LOWEST = -50 #Player wont move after this
    def __init__(self, name, x, y, team, acceleration, run_speed, walk_speed, strength, duration, dex, mass = 60):
        self.name = name
        self.x = x
        self.y = y

        self.team = team

        # Physical attributes
        self.acceleration = acceleration # determent how fast the player can change speed or direction
        self.walk_speed = walk_speed # determent normal run speed
        self.run_speed = run_speed  # determent the max speed player
        self.strength = strength # determent the kick speed
        self.duration = duration  # determent how long player can run
        self.MAX_STAMINA = self.BASE_STAMINA*duration
        self.stamina = self.BASE_STAMINA*duration
        self.dex = dex # this will determent
        self.mass = mass


        # Movement state
        self.vel_x = 0
        self.vel_y = 0
        self.is_running = False
        self.radius = 20

    def _apply_exhaust_penalty(self, base_value):
        if self.stamina > 0:
            return base_value
        elif self.stamina < self.BASE_STAMINA_LOWEST:
            return 0
        else:
            return base_value * self.EXHAUST_PENALTY_FACTOR

    def get_speed(self):
        if self.is_running:
            return self._apply_exhaust_penalty(self.run_speed)
        else:
            return self._apply_exhaust_penalty(self.walk_speed)

    def update(self,world, dt, dx, dy): #dx=-1 left, dý = down
        self.update_stamina(dt,dx,dy)
        self.update_speed(dt,dx,dy)
        self.move_to(world, dt)
    def update_speed(self,dt,dx,dy):
        if dx == 0:
            self.vel_x *= 0.8

        if dy == 0:
            self.vel_y *= 0.8

        # Normalize direction to prevent faster diagonal acceleration
        if dx != 0 or dy != 0:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length
            acc = self.acceleration * (2 if self.is_running else 1)

            ax = acc * dx * dt * 100
            ay = acc * dy * dt * 100

            # Clamp acceleration magnitude
            acc_magnitude = math.hypot(ax, ay)
            max_acc = self.acceleration * dt * 100
            if acc_magnitude > max_acc:
                scale = max_acc / acc_magnitude
                ax *= scale
                ay *= scale

            self.vel_x += ax
            self.vel_y += ay

        # Compute resulting speed
        speed = math.hypot(self.vel_x, self.vel_y)
        max_speed = self.get_speed()

        # Clamp speed if it exceeds max
        if speed > max_speed:
            scale = max_speed / speed
            self.vel_x *= scale
            self.vel_y *= scale
        if abs(self.vel_x) < 0.1: self.vel_x = 0
        if abs(self.vel_y) < 0.1: self.vel_y = 0

    def update_stamina(self,dt,dx,dy):
        if dx == 0 and dy == 0:
            if self.stamina < self.MAX_STAMINA - self.BASE_STAMINA_RECOVER * dt:
                self.stamina += self.BASE_STAMINA_RECOVER * dt
        elif self.is_running:
            self.stamina -= self.BASE_STAMINA_REDUCE_RUNNING * dt
        else:
            self.stamina -= self.BASE_STAMINA_REDUCE_WALKING * dt

    def move_to(self,world, dt):
        self.handle_collision(world.players)

        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
    def draw(self, surface):
        pygame.draw.circle(surface, self.team.colour, (int(self.x), int(self.y)), self.radius)
    def handle_collision(self, players):
        for other in players:
            if other is self:
                continue

            dx = other.x - self.x
            dy = other.y - self.y
            dist = math.hypot(dx, dy)
            min_dist = self.radius + other.radius

            if dist < min_dist and dist > 0:
                # Normalize direction vector
                nx = dx / dist
                ny = dy / dist

                # Relative velocity
                dvx = self.vel_x - other.vel_x
                dvy = self.vel_y - other.vel_y
                vn = dvx * nx + dvy * ny

                if vn > 0:
                    continue  # Already separating

                # Elastic collision response
                m1, m2 = self.mass, other.mass
                impulse = (-(1 + 1) * vn) / (1 / m1 + 1 / m2)

                self.vel_x += (impulse * nx) / m1
                self.vel_y += (impulse * ny) / m1
                other.vel_x -= (impulse * nx) / m2
                other.vel_y -= (impulse * ny) / m2

                # Push players apart (positional correction)
                overlap = min_dist - dist
                correction = overlap / (1 / m1 + 1 / m2)
                self.x -= correction * nx / m1
                self.y -= correction * ny / m1
                other.x += correction * nx / m2
                other.y += correction * ny / m2
