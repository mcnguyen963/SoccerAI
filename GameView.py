class GameView:
    def __init__(self, screen, field, players):
        self.screen = screen
        self.field = field
        self.players = players  # list of players

    def render(self):
        # Fill background
        self.screen.fill(self.field.colour)

        # Draw field
        self.field.draw(self.screen)

        # Draw all players
        for player in self.players:
            player.draw(self.screen)
