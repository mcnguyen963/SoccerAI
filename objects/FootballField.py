import pygame
class FootballField:
    def __init__(self, name, length, width, colour= None):
        self.name = name
        self.length = length
        self. width = width
        self.colour = colour

    def draw(self, surface):
        # Draw red boundary lines
        red = (0, 255, 0)
        pygame.draw.rect(surface, red, pygame.Rect(0, 0, self.length, self.width), width=3)


