import gym
import pygame
import random
import math
import cv2
from objects.FootballField import FootballField
from objects.FootballPlayer import FootballPLayer
from objects.FootballTeam import FootballTeam
from objects.FootballBall import FootballBall
from controller.PlayerController import PlayerController
from gym import spaces
import numpy as np

class FootBallGameEnv(gym.Env):
    OFF_SET = 50  # SPACING FROM TOP RIGHT
    TARGET_GOAL_VALUE = 10  # value determine the vicotry team
    MAX_GAME_DURATION = 30  # seconds
    SCALE = 1
    WINDOW_LENGTH = 1080
    WINDOW_WIDTH = 720
    TARGET_FPS = 120
    SIMPLE_MOVEMENT = [
        ['NOOP'],
        ['left'],
        ['right'],
        ['up'],
        ['down'],
        ['up', 'left'],
        ['up', 'right'],
        ['down', 'left'],
        ['down', 'right']
    ]
    def __init__(self,observation_mode = 'data'):
        # value represent in SIMPLE_MOVEMENT
        self.action_space = spaces.Discrete(9)
        self.observation_mode = observation_mode
        if self.observation_mode == 'visual':
            obs_width = int(self.WINDOW_LENGTH * self.SCALE)
            obs_height = int(self.WINDOW_WIDTH * self.SCALE)
            self.observation_space = spaces.Box(
                low=0,
                high=255,
                shape=(obs_height, obs_width, 3),
                dtype=np.uint8
            )
        else:
            self.observation_space = spaces.Box(
                low=-float('inf'),
                high=float('inf'),
                shape=(11, 5),
                dtype=np.float32
            )
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
        self.add_random_players()

        self.player_controller = PlayerController(self)
        self.screen = pygame.display.set_mode(
            (self.field.length + self.OFF_SET * 2 * self.SCALE, self.field.width + self.OFF_SET * 2 * self.SCALE))
        pygame.display.set_caption("Soccer game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.number_allowable_time_second = self.MAX_GAME_DURATION
    def step(self, action,  player_index = 0):
        default_player = self.players[player_index]
        dt = self.clock.tick(self.TARGET_FPS) / 1000.0
        self.number_allowable_time_second -= dt
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
        if len(self.balls)>0:
            self.balls[0].update(self,dt)
        # for each other aciton/
        # update them
        # Compute reward and check for terminal condition
        if self.observation_mode == "visual":
            state = self.render(mode="rgb_array")  # H×W×3 frame
        else:
            state = self.get_state(default_player)
        reward = self.get_reward(default_player)
        done = self.get_winning_team() is not None or self.number_allowable_time_second <= 0
        info = {
            "player_position": (default_player.x, default_player.y),
            "ball_count": len(self.balls),
            "winning_team": self.get_winning_team()
        }
        return state, reward, done, info

    def render(self, mode="human"):
        team_score_distant = 0

        for team in self.teams:
            team.draw(self.screen, (team_score_distant, 0), self.SCALE)
            team_score_distant +=  300*self.SCALE

        for object in self.objects:
            object.draw(self.screen)
        pygame.display.flip()

        if mode == "rgb_array":
            frame = pygame.surfarray.array3d(self.screen)
            frame = np.transpose(frame, (1, 0, 2))  # (W, H, C) → (H, W, C)

            # Resize to match the observation_space
            frame = cv2.resize(frame, (270, 180))  # width x height
            return frame
        if len(self.players) >0:
            return self.get_reward(self.players[0])
        return None
    def reset(self):
        self.players = []
        self.collidable_objects = [self.balls[0]]
        self.team_a.score = 0
        self.team_b.score =0
        self.teams = [self.team_a, self.team_b]

        self.balls[0].reset_ball_position()
        self.objects.append(self.balls[0])
        self.add_random_players()
        self.running = True
        self.number_allowable_time_second = self.MAX_GAME_DURATION
        return self.get_state(self.players[0])

    # update the visual for the game
    def render_game_view(self):
        # Fill background with field colour
        self.screen.fill(self.field.colour)
        distant_between_team_score = 300

        # display the score for each team
        for team in self.teams:
            team.draw(self.screen, (distant_between_team_score, 0), self.SCALE)
            distant_between_team_score += distant_between_team_score * self.SCALE

        # call the draw methods for each drawable_object
        for object in self.objects:
            object.draw(self.screen)

    def add_player(self, player):
        self.players.append(player)
        self.objects.append(player)
        self.collidable_objects.append(player)
    def create_random_player(self,team,is_bot):
        return FootballPLayer(
            name=str(random.uniform(1,2)),
            x=random.randint(int(self.OFF_SET * self.SCALE),
                             int(self.field.length + self.OFF_SET * self.SCALE)),
            y=random.randint(int(self.OFF_SET * self.SCALE),
                             int(self.field.width + self.OFF_SET * self.SCALE)),
            team=team,
            acceleration=float(600 * random.uniform(0.8, 1.1)),
            run_speed=float(600 * random.uniform(0.8, 1.1)),
            walk_speed=float(800 * random.uniform(0.8, 1.1)),
            strength=float(random.uniform(1, 1.9)),
            stamina=float(300 * random.uniform(1, 1.3)),
            dex=float(random.uniform(1, 1.3)),
            mass=float(60 * random.uniform(0.8, 1.5)),
            is_bot= is_bot,
            window_scale=self.SCALE
                                     )
    # add a random player in pair for each team.
    def add_random_players(self):
        MAX_PER_TEAM = 5
        for i in range(MAX_PER_TEAM):
            # create a player the first player's team is random so the AI can learn for both team
            random_value =  random.randint(1,2)
            player = self.create_random_player(team=self.team_a if random_value==1 else self.team_b,is_bot=True)
            self.add_player(player)
            player = self.create_random_player(team=self.team_a if random_value==2 else self.team_b,is_bot=True)
            self.add_player(player)

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

    def get_state(self, player):
        state = []

        # Ball info: team_side = 0.0 for ball (neutral)
        each_ball = self.balls[0]
        state.append([0.0, each_ball.x, each_ball.y, each_ball.vel_x, each_ball.vel_y])

        # The current player
        team_value = 1.0 if not player.team.is_on_left_side else -1.0
        state.append([team_value, player.x, player.y, player.vel_x, player.vel_y])

        # Other players
        for each_player in self.players:
            if each_player is not player:
                team_value = 1.0 if not each_player.team.is_on_left_side else -1.0
                state.append([team_value, each_player.x, each_player.y, each_player.vel_x, each_player.vel_y])

        # Convert to np.array of shape (11, 5) and dtype float32
        state_array = np.array(state, dtype=np.float32)

        # Just to be safe, you can check and pad or truncate if necessary
        if state_array.shape != (11, 5):
            raise ValueError(f"State shape mismatch! Expected (11,5), got {state_array.shape}")
        return state_array

    # def get_state(self, player):
    #     state = []
    #
    #     # Ball info: team_side = 0.0 for ball (neutral)
    #     each_ball = self.balls[0]
    #     state.append([0.0, each_ball.x, each_ball.y, each_ball.vel_x, each_ball.vel_y])
    #
    #     # The current player
    #     team_value = 1.0 if not player.team.is_on_left_side else -1.0
    #     state.append([team_value, player.x, player.y, player.vel_x, player.vel_y])
    #
    #     # Other players
    #     for each_player in self.players:
    #         if each_player is not player:
    #             team_value = 1.0 if not each_player.team.is_on_left_side else -1.0
    #             state.append([team_value, each_player.x, each_player.y, each_player.vel_x, each_player.vel_y])
    #
    #     # Convert to np.array of shape (11, 5) and dtype float32
    #     state_array = np.array(state, dtype=np.float32)
    #     print(state_array)
    #     # Just to be safe, you can check and pad or truncate if necessary
    #     if state_array.shape != (11, 5):
    #         raise ValueError(f"State shape mismatch! Expected (11,5), got {state_array.shape}")
    #
    #     return state_array
    def get_winning_team(self):
        for team in self.teams:
            if team.score >= self.TARGET_GOAL_VALUE:
                return team
        return None