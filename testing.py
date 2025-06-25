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
import numpy as np
import math
import cv2

class World(gym.Env):
    OFF_SET = 50  # SPACING FROM TOP RIGHT
    TARGET_GOAL_VALUE = 10  # value determine the vicotry team
    MAX_GAME_DURATION = 180  # seconds
    SCALE = 1
    WINDOW_LENGTH = 1080
    WINDOW_WIDTH = 720
    TARGET_FPS = 120
    # gym env attribute
    metadata = {"render.modes": ["human", "rgb_array"], "video.frames_per_second": TARGET_FPS}
    continuous = True

    def __init__(self):
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
        # left,right,up,down and is running for each direction
        self.action_space = spaces.Discrete(8)
        obs_width = int(self.WINDOW_LENGTH * self.SCALE)
        obs_height = int(self.WINDOW_WIDTH * self.SCALE)
        self.observation_space = spaces.Box(
            low=0,
            high=255,
            shape=(obs_height, obs_width, 3),  # (H, W, C)
            dtype=np.uint8
        )

    def add_player(self, player):
        self.players.append(player)
        self.objects.append(player)
        self.collidable_objects.append(player)

    def add_player_from_file(self, file_path="/Users/nguyen/PycharmProjects/footballAI/data/players.txt"):
        try:
            with open(file_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    player = FootballPLayer(
                        name=row["name"],
                        x=random.randint(int(self.OFF_SET * self.SCALE),
                                         int(self.field.length + self.OFF_SET * self.SCALE)),
                        y=random.randint(int(self.OFF_SET * self.SCALE),
                                         int(self.field.width + self.OFF_SET * self.SCALE)),
                        team=self.team_b if row["team_name"] == self.team_b.name else self.team_a,
                        acceleration=float(600*random.randint(100,110)/100),
                        run_speed=float(600*random.randint(100,110)/100),
                        walk_speed=float(800*random.randint(100,110)/100),
                        strength=float(random.randint(100,200)/100),
                        stamina=float(300*random.randint(100,200)/100),
                        dex=float(row["dex"]),
                        mass=float(row["mass"]),
                        is_bot=row["is_bot"].lower() == "true",
                        window_scale=self.SCALE
                    )
                    self.add_player(player)

        except FileNotFoundError:
            print(f"File {file_path} not found.")
        except Exception as e:
            print(f"Error loading players from file: {e}")

    def run(self):

        start_time = pygame.time.get_ticks()  # start_time
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
        self.view.render()
        pygame.display.flip()
        return self.render(mode="rgb_array")

    def step(self, action, player_index = 0):
        default_player = self.players[player_index]
        dt = self.clock.tick(self.TARGET_FPS) / 1000.0

        dx, dy = 0, 0
        if action == 1:  # left
            dx = -1
        elif action == 2:  # right
            dx = 1
        elif action == 3:  # up
            dy = -1
        elif action == 4:  # down
            dy = 1
        elif action == 5:  # up-left
            dx = -1
            dy = -1
        elif action == 6:  # up-right
            dx = 1
            dy = -1
        elif action == 7:  # down-left
            dx = -1
            dy = 1
        elif action == 8:  # down-right
            dx = 1
            dy = 1

        # Update game state
        default_player.update(self, dt, dx, dy)
        self.player_controller.ball_controller(dt, self.balls)
        self.view.render()

        # Compute reward and check for terminal condition
        reward = self.get_reward(default_player)
        done = self.get_winning_team() is not None

        # Render and get new observation (state)
        self.render()
        state = self.render(mode="rgb_array")

        info = {
            "player_position": (default_player.x, default_player.y),
            "ball_count": len(self.balls),
            "winning_team": self.get_winning_team()
        }

        return state, reward, done, info
    def get_reward(self, player):
        ball = self.balls[0]
        target_goal_x = self.OFF_SET * self.SCALE+self.field.length
        player_team = self.team_b
        opponent_team = self.team_a
        if player.team.is_on_left_side:
            player_team = self.team_a
            opponent_team = self.team_b
            target_goal_x = self.OFF_SET*self.SCALE

        target_goal_y = (self.field.goal_y_end + self.field.goal_y_start)/2
        distant_score = -1* math.dist([player.x,player.y],[ball.x,ball.y])
        if player_team.is_on_left_side and player.x > ball.x or not player_team.is_on_left_side and player.x<ball.x:
            distant_score -= self.field.length/2

        k_value =distant_score
        k_value += math.dist([ball.x,ball.y],[target_goal_x,target_goal_y])
        k_value += self.field.length*(player_team.score-opponent_team.score)
        return k_value
    def close(self):
        pygame.quit()

    def get_observation(self):
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
            self.view.render()
            pygame.display.flip()
            frame = pygame.surfarray.array3d(self.screen)
            frame = np.transpose(frame, (1, 0, 2))  # (W, H, C) → (H, W, C)

            # Resize to match the observation_space
            frame = cv2.resize(frame, (270, 180))  # width x height
            return frame
        else:
            raise NotImplementedError(f"Render mode {mode} not supported")


