import pygame
from objects.FootballField import FootballField
from objects.FootballPlayer import FootballPLayer
from objects.FootballTeam import FootballTeam
from objects.FootballBall import FootballBall
from controller.PlayerController import PlayerController
from GameView import GameView
import math
class World:
    def __init__(self):
        pygame.init()

        # Create field and set color
        self.field = FootballField("Main Field", 1000, 1000)
        self.field.colour = (0, 0, 0)  # Black

        # Create teams
        self.team_white = FootballTeam("White Team", (255, 0, 0))
        self.team_red = FootballTeam("Red Team", (0, 0, 255))
        self.ball = FootballBall(500, 500)

        # Create players
        self.player1 = FootballPLayer(
            "Player 1", 500, 500,
            team=self.team_white,
            acceleration=7,
            run_speed=500,
            walk_speed=300,
            strength=3,
            duration=10,
            dex=0.8, mass = 6000
        )

        self.player2 = FootballPLayer(
            "Player 2", 600, 500,
            team=self.team_red,
            acceleration=0.6,
            run_speed=4.5,
            walk_speed=2.5,
            strength=4,
            duration=1.3,
            dex=0.7, mass = 10
        )

        self.bot_players = [self.player2]
        self.players = [self.player1,self.player2]
        self.objects=[self.player1,self.player2, self.ball]

        # Controllers
        self.player_controller = PlayerController(self)

        # Pygame screen setup
        self.screen = pygame.display.set_mode((self.field.length, self.field.width))
        pygame.display.set_caption("Modular Drawing with View")

        # View
        self.view = GameView(self.screen, self.field, self.objects)

        # Clock
        self.clock = pygame.time.Clock()

        # Running flag
        self.running = True

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # seconds passed

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Update controllers
            self.player_controller.player_controller(dt, self.player1)
            self.player_controller.bot_controller(dt, self.bot_players)


            # Render view
            self.view.render()

            pygame.display.flip()
            # You can remove this second clock.tick(60) call; it's redundant

        pygame.quit()
