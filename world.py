import pygame
from objects.FootballField import FootballField
from objects.FootballPlayer import FootballPLayer
from objects.FootballTeam import FootballTeam
from objects.FootballBall import FootballBall
from controller.PlayerController import PlayerController
from GameView import GameView
import math
class World:
    OFF_SET = 50 #SPACING FROM TOP RIGHT
    def __init__(self):
        pygame.init()
        self.objects=[]
        self.players = []
        self.teams=[]
        self.balls = []

        self.collidable_objects=[]
        # Create field and set color
        self.field = FootballField("Main Field", 1000, 700, (0,0,0,0),self.OFF_SET)
        self.field.colour = (0, 0, 0)
        self.objects.append(self.field)

        # Create teams
        self.team_a = FootballTeam("A Team", (255, 0, 0))
        self.teams.append(self.team_a)

        self.team_b = FootballTeam("B Team", (0, 0, 255), is_on_left_side=False)
        self.teams.append(self.team_b)

        # Create ball
        ball = FootballBall(self.field.length/2+self.OFF_SET, self.field.width/2+self.OFF_SET, mass=10)

        self.balls.append(ball)
        self.objects.append(ball)
        self.collidable_objects.append(ball)

        # Create players
        self.add_player(FootballPLayer(
            "Player 1", 400, 500,
            team=self.team_a,
            acceleration=7,
            is_bot = False,
            run_speed=500,
            walk_speed=300,
            strength=1.5,
            duration=10,
            dex=0.8, mass = 60
        ))
        self.add_player(FootballPLayer(
            "Player 2", 600, 500,
            team=self.team_b,
            acceleration=0.6,
            run_speed=4.5,
            walk_speed=2.5,
            strength=1.9,
            duration=1.3,
            dex=0.7, mass = 60
        ))

        # Controllers
        self.player_controller = PlayerController(self)

        # Pygame screen setup
        self.screen = pygame.display.set_mode((self.field.length+self.OFF_SET*2, self.field.width+self.OFF_SET*2))
        pygame.display.set_caption("Modular Drawing with View")

        # View
        self.view = GameView(self.screen, self)

        # Clock
        self.clock = pygame.time.Clock()

        # Running flag
        self.running = True
    def add_player(self, player):
        self.players.append(player)
        self.objects.append(player)
        self.collidable_objects.append(player)


    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # seconds passed

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Update controllers

            for player in self.players:
                if player.is_bot:
                    self.player_controller.bot_controller(dt, player)
                else:
                    self.player_controller.player_controller(dt, player)

            self.player_controller.ball_controller(dt, self.balls)

            # Render view
            self.view.render()

            pygame.display.flip()
            # You can remove this second clock.tick(60) call; it's redundant

        pygame.quit()
