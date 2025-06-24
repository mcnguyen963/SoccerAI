import pygame
class FootballField:
    def __init__(self, name, length, width, colour= (255,255,255), offset = 0, scale = 1):
        self.name = name
        self.length = length
        self.width = width
        self.colour = colour
        self.offset = offset*scale
        self.scale =scale

        self.goal_width = self.width // 4
        self.goal_y_start = (self.width - self.goal_width) // 2 + self.offset
        self.goal_y_end = self.goal_y_start + self.goal_width

        # Store goal positions as tuples (x, y_start, y_end)
        self.left_goal_pos = (self.offset, self.goal_y_start, self.goal_y_end)
        self.right_goal_pos = (self.length + self.offset, self.goal_y_start, self.goal_y_end)

    def draw(self, surface):
        # Draw red boundary lines
        red = (0, 255, 0)
        pygame.draw.rect(surface, red, pygame.Rect(self.offset, self.offset, self.length, self.width), width=3)

        white = (255, 255, 255)
        goal_width = self.width // 4
        goal_y_start = (self.width - goal_width) // 2+self.offset
        goal_y_end = goal_y_start + goal_width

        # Left goal line
        pygame.draw.line(surface, white, (self.left_goal_pos[0], self.left_goal_pos[1]), (self.left_goal_pos[0], self.left_goal_pos[2]), width=4)

        # Right goal line
        pygame.draw.line(surface, white, (self.right_goal_pos[0], self.right_goal_pos[1]), (self.right_goal_pos[0], self.right_goal_pos[2]), width=4)

