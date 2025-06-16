class GameView:
    def __init__(self, screen, world):
        self.screen = screen
        self.world = world


    def render(self):
        # Fill background
        self.screen.fill(self.world.field.colour)  # Grass background
        counter = 0
        for team in self.world.teams:
            team.draw(self.screen,(counter,0))
            counter+= 300
        # Draw all players
        for object in self.world.objects:
            object.draw(self.screen)
