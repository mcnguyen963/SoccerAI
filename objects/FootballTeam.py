import pygame
class FootballTeam:
    def __init__(self, name, colour = (0,0,0), is_on_left_side=True):
        self.name = name
        self.colour = colour
        self.score = 0
        self.is_on_left_side = is_on_left_side

    def draw(self, surface, position, window_scale):
        font = pygame.font.SysFont(None, int(40*window_scale))
        text = f"{self.name}: {self.score}"
        rendered_text = font.render(text, True, self.colour)
        surface.blit(rendered_text, position)