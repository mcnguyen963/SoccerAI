import pygame
from objects.FootballField import FootballField
from objects.FootballPlayer import FootballPLayer
from objects.FootballTeam import FootballTeam
from objects.FootballBall import FootballBall
from controller.PlayerController import PlayerController
from GameView import GameView
import random
import csv
import gym
from gym import spaces
import math
class World (gym.Env):
    OFF_SET = 50 # SPACING FROM TOP RIGHT
    TARGET_GOAL_VALUE = 10 # value determine the vicotry team
    MAX_GAME_DURATION = 180  # seconds
    SCALE = 0.25
    WINDOW_LENGTH = 1080
    WINDOW_WIDTH = 720
    TARGET_FPS = 120
    # gym env attribute
    metadata = {"render.modes": ["human", "rgb_array"], "video.frames_per_second": FPS}
    continuous = True

    def __init__(self):
        pygame.init()
        self.objects=[]
        self.players = []
        self.teams=[]
        self.balls = []
        self.collidable_objects=[]

        # Create field and set color
        background_colour = (0,0,0) # black
        self.field = FootballField("Main Field", self.WINDOW_LENGTH*self.SCALE, self.WINDOW_WIDTH*self.SCALE, background_colour,self.OFF_SET,self.SCALE)
        self.objects.append(self.field)

        # Create teams
        self.team_a = FootballTeam("A Team", (255, 0, 0))
        self.teams.append(self.team_a)

        self.team_b = FootballTeam("B Team", (0, 0, 255), is_on_left_side=False)
        self.teams.append(self.team_b)

        # Create ball in middle of the field, this also the reset location for the ball
        ball = FootballBall(self.field.length/2+self.OFF_SET*self.SCALE, self.field.width/2+self.OFF_SET*self.SCALE, mass=10,window_scale=self.SCALE)
        self.balls.append(ball)
        self.objects.append(ball)
        self.collidable_objects.append(ball)

        #add player from player.txt
        self.add_player_from_file()

        self.player_controller = PlayerController(self)

        self.screen = pygame.display.set_mode((self.field.length+self.OFF_SET*2*self.SCALE, self.field.width+self.OFF_SET*2*self.SCALE))
        pygame.display.set_caption("Soccer game")

        self.view = GameView(self.screen, self)

        self.clock = pygame.time.Clock()

        self.running = True
        # left,right,up,down and is running for each direction
        self.action_space = spaces.Discrete(8)

    def add_player(self, player):
        self.players.append(player)
        self.objects.append(player)
        self.collidable_objects.append(player)
    def add_player_from_file(self, file_path="data/players.txt"):
        try:
            with open(file_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:

                    player = FootballPLayer(
                        name=row["name"],
                        x=random.randint(int(self.OFF_SET*self.SCALE),int(self.field.length+self.OFF_SET*self.SCALE)),
                        y=random.randint(int(self.OFF_SET*self.SCALE),int(self.field.width+self.OFF_SET*self.SCALE)),
                        team=self.team_b if row["team_name"] == self.team_b.name else self.team_a,
                        acceleration=float(row["acceleration"]),
                        run_speed=float(row["run_speed"]),
                        walk_speed=float(row["walk_speed"]),
                        strength=float(row["strength"]),
                        stamina=float(row["stamina"]),
                        dex=float(row["dex"]),
                        mass=float(row["mass"]),
                        is_bot=row["is_bot"].lower() == "true",
                        window_scale = self.SCALE
                    )
                    self.add_player(player)

        except FileNotFoundError:
            print(f"File {file_path} not found.")
        except Exception as e:
            print(f"Error loading players from file: {e}")

    def run(self):

        start_time = pygame.time.get_ticks()#start_time
        while self.running and self.get_winning_team() is None:
            dt = self.clock.tick(self.TARGET_FPS) / 1000.0  # calculate time per frame

            # End game if it reaches time limit
            if (pygame.time.get_ticks() - start_time) / 1000.0 >= self.MAX_GAME_DURATION:
                print("Time limit reached.")
                break
            # End the game if user action such as close window is click
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Call the controller for each player to get their action per frame
            for player in self.players:
                if player.is_bot:
                    self.player_controller.bot_controller(dt, player)
                else:
                    self.player_controller.player_controller(dt, player)

            self.player_controller.ball_controller(dt, self.balls)
            # Render view
            self.view.render()
            pygame.display.flip()
        return self.get_winning_team()
        pygame.quit()
    def get_winning_team(self):
        for team in self.teams:
            if team.score >= self.TARGET_GOAL_VALUE:
                return team
        return None
    def get_state(self):
        surface = pygame.display.get_surface()
        frame = pygame.surfarray.array3d(surface)

        return frame

    def reset(self):
        """Resets the environment to an initial state and returns an initial
        observation.

        Note that this function should not reset the environment's random
        number generator(s); random variables in the environment's state should
        be sampled independently between multiple calls to `reset()`. In other
        words, each call of `reset()` should yield an environment suitable for
        a new episode, independent of previous episodes.

        Returns:
            observation (object): the initial observation.
        """
        pygame.init()
        self.objects = []
        self.players = []
        self.teams = []
        self.balls = []
        self.collidable_objects = []

        # Create field and set color
        background_colour = (0, 0, 0)  # black
        self.field = FootballField("Main Field", self.WINDOW_LENGTH * self.SCALE, self.WINDOW_WIDTH * self.SCALE,
                                   background_colour, self.OFF_SET, self.SCALE)
        self.objects.append(self.field)

        # Create teams
        self.team_a = FootballTeam("A Team", (255, 0, 0))
        self.teams.append(self.team_a)

        self.team_b = FootballTeam("B Team", (0, 0, 255), is_on_left_side=False)
        self.teams.append(self.team_b)

        # Create ball in middle of the field, this also the reset location for the ball
        ball = FootballBall(self.field.length / 2 + self.OFF_SET * self.SCALE,
                            self.field.width / 2 + self.OFF_SET * self.SCALE, mass=10, window_scale=self.SCALE)
        self.balls.append(ball)
        self.objects.append(ball)
        self.collidable_objects.append(ball)

        # add player from player.txt
        self.add_player_from_file()

        self.player_controller = PlayerController(self)

        self.screen = pygame.display.set_mode(
            (self.field.length + self.OFF_SET * 2 * self.SCALE, self.field.width + self.OFF_SET * 2 * self.SCALE))
        pygame.display.set_caption("Soccer game")

        self.view = GameView(self.screen, self)

        self.clock = pygame.time.Clock()

        self.running = True

    def step(self, action):
        default_player = self.players[0]
        SIMPLE_MOVEMENT = [['left'], ['right'], ['up'], ['down']]
        dt = 1 / self.TARGET_FPS  # fixed timestep

        for player in self.players:
            if player.is_bot:
                self.player_controller.bot_controller(dt, player)
            else:
                self.player_controller.player_controller(dt, player)

        self.player_controller.ball_controller(dt, self.balls)

        self.view.render()
        pygame.display.flip()
        self.clock.tick(self.TARGET_FPS)

        # Compute reward: e.g., +1 if your team scored, 0 otherwise
        reward = 0
        done = False
        info = {}

        winner = self.get_winning_team()
        if winner is not None:
            done = True
            reward = 1 if winner == self.team_a else -1  # example reward

        # Observation: you must implement a proper observation representing environment state
        observation = self._get_observation()

        return observation, reward, done, info


    def close(self):
        pygame.quit()

    def _get_observation(self):
        # Return a numpy array or object that represents the environment's current observation
        # This is a placeholder example: positions (x,y) of all players + ball
        import numpy as np

        obs = []
        for player in self.players:
            obs.extend([player.x, player.y])
        for ball in self.balls:
            obs.extend([ball.x, ball.y])

        return np.array(obs, dtype=float)
    def render(self, mode="human"):
        if mode == "human":
            self.view.render()
            pygame.display.flip()
        elif mode == "rgb_array":
            return pygame.surfarray.array3d(self.screen)
        else:
            raise NotImplementedError(f"Render mode {mode} not supported")


