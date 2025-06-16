import pygame
class FootballTeam:
    def __init__(self, name, colour = (0,0,0)):
        self.name = name
        self.colour = colour
        self.score = 0

    def draw(self, surface, position):
        font = pygame.font.SysFont(None, 40)
        text = f"{self.name}: {self.score}"
        rendered_text = font.render(text, True, self.colour)
        surface.blit(rendered_text, position)