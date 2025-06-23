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
        # player.is_running = False
        #
        # goal_y_start = self.world.field.goal_y_start
        # goal_y_end = self.world.field.goal_y_end
        # distant_to_ball = math.hypot(player.x - ball.x, player.y - ball.y)
        #
        # field_width = self.world.field.width
        # is_left_side = player.team.is_on_left_side
        # if is_left_side:
        #     own_goal_x = self.world.OFF_SET
        #     opponent_goal_x = field_width + self.world.OFF_SET
        # else:
        #     own_goal_x = field_width + self.world.OFF_SET
        #     opponent_goal_x = self.world.OFF_SET
        #
        # ball_speed = (ball.vel_x ** 2 + ball.vel_y ** 2) ** 0.5
        # player_speed = (player.vel_x ** 2 + player.vel_y ** 2) ** 0.5
        #
        # is_in_danger_zone = goal_y_start <= self.get_kick_target(own_goal_x, player.x, player.y, ball.x,
        #                                                          ball.y) <= goal_y_end and (is_left_side and player.x<=ball.x or not is_left_side and player.x>=ball.x)
        # is_in_good_zone = goal_y_start <= self.get_kick_target(opponent_goal_x, player.x, player.y, ball.x,
        #                                                        ball.y) <= goal_y_end and (is_left_side and player.x<=ball.x or not is_left_side and player.x>=ball.x)
        #
        # dx, dy = 0, 0  # default
        # if is_in_danger_zone:
        #     print('danager')
        #     if abs(player.y - ball.y) < 30:
        #         if player.y > self.world.OFF_SET + player.radius + 10:
        #             dy = -1
        #         else:
        #             dy = 1
        #     else:
        #         if is_left_side:
        #             dx = -1
        #         else:
        #             dx = 1
        #
        # elif is_in_good_zone:
        #     print('safe')
        #     if ball.x > player.x:
        #         dx = 1
        #     elif ball.x < player.x:
        #         dx = -1
        #     if ball.y > player.y:
        #         dy = 1
        #     elif ball.y < player.y:
        #         dy = -1
        #     player.is_running = True
        # else:
        #     print('going')
        #
        #     if is_left_side:
        #         if player.x < ball.x - ball.radius - player.radius - 10:
        #             if player.y< ball.y:
        #                 dy=0.1
        #                 dx=0
        #             if player.y > ball.y:
        #                 dy=-0.1
        #                 dx=0
        #             if player.y == ball.y:
        #                 dy=0
        #                 dx=1
        #
        #
        #         if player.x >= ball.x - ball.radius - player.radius - 10:
        #             if abs(player.y-ball.y)<= player.radius + ball.radius:
        #                 if player.y> player.radius:
        #                     dy=-1
        #                     dx=0
        #                 else:
        #                     dy=1
        #                     dx=0
        #             else:
        #                 dx =-1
        #                 dy=0
        #     else:
        #         if player.x > ball.x + ball.radius + player.radius + 10:
        #             dx = 1
        #             if player.y > ball.y:
        #                 dy = -1
        #             elif player.y < ball.y:
        #                 dy = 1
        #         if player.x <= ball.x + ball.radius + player.radius + 10 and abs(ball.y - player.y) > 50:
        #             dx = 1
        #             dy = 0
        #         elif player.x <= ball.x and abs(ball.y - player.y) > 50:
        #             dx = 0
        #             if player.y < self.world.field.width + self.world.OFF_SET:
        #                 dy = 1
        #             else:
        #                 dy = -1
        #
        player.update(self.world, dt, dx, dy)


    def get_kick_target(self, x_value, current_x, current_y, target_x, target_y):
        slope = (target_y - current_y) / (target_x - current_x)
        intercept = current_y - slope * current_x
        y_value = slope * x_value + intercept
        return y_value

    def ball_controller(self, dt, balls):
        for ball in balls:
            ball.update(self.world, dt)
