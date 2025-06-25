class GameView:
    def __init__(self, screen, world):
        self.screen = screen
        self.world = world


    def render(self):
        # Fill background
        self.screen.fill(self.world.field.colour)
        counter = 0
        for team in self.world.teams:
            team.draw(self.screen,(counter,0),self.world.SCALE)
            counter+= 300*self.world.SCALE

        for object in self.world.objects:
            object.draw(self.screen)
