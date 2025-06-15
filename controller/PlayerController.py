import pygame

class PlayerController:
    def __init__(self, world):
        self.world = world

    def player_controller(self,dt, player):
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
        print(dx,dy)
        player.update(self.world, dt,dx,dy)
        # Clamp inside field boundaries
        player.x = max(0, min(self.world.field.length, player.x))
        player.y = max(0, min(self.world.field.width, player.y))

    def bot_controller (self,dt, players):
        for player in players:
            dx = 0
            dy = 0
            player.update(self.world, dt, dx, dy)
            player.x = max(0, min(self.world.field.length, player.x))
            player.y = max(0, min(self.world.field.width, player.y))
