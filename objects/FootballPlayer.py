import pygame
import sys
import math

class FootballPLayer:
    EXHAUST_PENALTY_FACTOR = 0.5
    BASE_STAMINA = 100
    BASE_STAMINA_REDUCE_RUNNING = 10
    BASE_STAMINA_REDUCE_WALKING = 4
    BASE_STAMINA_RECOVER = 6
    BASE_STAMINA_LOWEST = -50#Player wont move after this
    BASE_SPEED_REDUCE_RATE = 0.99
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
        self.move_to( dt)
        self.handle_collisions(world.players)
    def update_speed(self,dt,dx,dy):
        if dx == 0:
            self.vel_x *= self.BASE_SPEED_REDUCE_RATE

        if dy == 0:
            self.vel_y *= self.BASE_SPEED_REDUCE_RATE

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

    def move_to(self, dt):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt

    def draw(self, surface):
        pygame.draw.circle(surface, self.team.colour, (int(self.x), int(self.y)), self.radius-2)
        line_length = 30  # Length of the line
        speed = math.hypot(self.vel_x, self.vel_y)
        if speed > 0.1:  # Only draw if player is moving
            dx = self.vel_x / speed
            dy = self.vel_y / speed
            end_x = self.x + dx * line_length
            end_y = self.y + dy * line_length

            # Draw the line
            pygame.draw.line(surface, (255, 255, 255), (int(self.x), int(self.y)), (int(end_x), int(end_y)), 2)
    def handle_collisions(self, all_players):
        for other_player in all_players:
            if other_player is self:  # Don't collide with self
                continue

            dx = self.x - other_player.x
            dy = self.y - other_player.y
            distance = math.hypot(dx, dy)
            min_distance = self.radius + other_player.radius

            if distance < min_distance and distance != 0:
                # Collision detected!
                # 1. Resolve overlap (push them apart)
                overlap = min_distance - distance
                # Move both players away from each other proportionally to their masses, or simply half each
                # For simplicity, let's just push them equally apart along the collision normal
                # This prevents them from getting stuck, but can look a bit "jerky"
                correction_x = dx / distance * overlap * 0.5
                correction_y = dy / distance * overlap * 0.5

                self.x += correction_x
                self.y += correction_y
                other_player.x -= correction_x
                other_player.y -= correction_y

                # 2. Resolve velocities (elastic collision)
                # Unit normal vector
                nx = dx / distance
                ny = dy / distance

                # Unit tangent vector
                tx = -ny
                ty = nx

                # Project velocities onto the normal and tangent vectors
                # Player 1 (self)
                v1n = self.vel_x * nx + self.vel_y * ny
                v1t = self.vel_x * tx + self.vel_y * ty

                # Player 2 (other_player)
                v2n = other_player.vel_x * nx + other_player.vel_y * ny
                v2t = other_player.vel_x * tx + other_player.vel_y * ty

                # Calculate new normal velocities (1D elastic collision formula)
                # v_final1 = (v1n * (m1 - m2) + 2 * m2 * v2n) / (m1 + m2)
                # v_final2 = (v2n * (m2 - m1) + 2 * m1 * v1n) / (m1 + m2)
                # Assuming equal mass for simplicity (m1=m2=m), this simplifies:
                # v_final1 = v2n
                # v_final2 = v1n
                # If masses are different:
                m1 = self.mass
                m2 = other_player.mass

                v1n_final = (v1n * (m1 - m2) + 2 * m2 * v2n) / (m1 + m2)
                v2n_final = (v2n * (m2 - m1) + 2 * m1 * v1n) / (m1 + m2)

                # Convert scalar normal and tangent velocities back to vectors
                self.vel_x = v1n_final * nx + v1t * tx
                self.vel_y = v1n_final * ny + v1t * ty

                other_player.vel_x = v2n_final * nx + v2t * tx
                other_player.vel_y = v2n_final * ny + v2t * ty

                # Add a small damping to prevent infinite bouncing or
                # to simulate some energy loss (optional)
                damping_factor = 1
                self.vel_x *= damping_factor
                self.vel_y *= damping_factor
                other_player.vel_x *= damping_factor
                other_player.vel_y *= damping_factor