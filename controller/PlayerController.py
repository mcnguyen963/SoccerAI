import pygame
import math


class PlayerController:
    def __init__(self, world):
        self.world = world

    def player_controller(self, dt, player):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LSHIFT]:
            player.is_running = True
        else:
            player.is_running = False
        dx = 0
        dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
        player.update(self.world, dt, dx, dy)
        print(self.world.get_reward(player))

    def bot_controller(self, dt, player):
        ball = self.world.balls[0]
        dx = dy=1
        if player.x> ball.x:
            dx = -1
        elif player.x < ball.x:
            dx =1
        if player.y > ball.y:
            dy = -1
        elif player.y < ball.y:
            dy = 1
        player.update(self.world, dt, dx, dy)


    def get_kick_target(self, x_value, current_x, current_y, target_x, target_y):
        slope = (target_y - current_y) / (target_x - current_x)
        intercept = current_y - slope * current_x
        y_value = slope * x_value + intercept
        return y_value

    def ball_controller(self, dt, balls):
        for ball in balls:
            ball.update(self.world, dt)
