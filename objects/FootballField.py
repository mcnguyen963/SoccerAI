import pygame
class FootballField:
    def __init__(self, name, length, width, colour= None, offset = 0):
        self.name = name
        self.length = length
        self.width = width
        self.colour = colour
        self.offset = offset


    def draw(self, surface):
        # Draw red boundary lines
        red = (0, 255, 0)
        pygame.draw.rect(surface, red, pygame.Rect(self.offset, self.offset, self.length, self.width), width=3)

        white = (255, 255, 255)
        goal_width = self.width // 4
        goal_y_start = (self.width - goal_width) // 2+self.offset
        goal_y_end = goal_y_start + goal_width

        # Left goal line
        pygame.draw.line(surface, white, (self.offset, goal_y_start), (self.offset, goal_y_end), width=4)

        # Right goal line
        pygame.draw.line(surface, white, (self.length + self.offset, goal_y_start), (self.length + self.offset, goal_y_end), width=4)

