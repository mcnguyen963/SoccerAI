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
from stable_baselines3.common.vec_env import VecFrameStack, DummyVecEnv

from stable_baselines3 import PPO
from gym import spaces
import numpy as np

class FootBallGameEnv(gym.Env):
    OFF_SET = 50  # SPACING FROM TOP RIGHT
    TARGET_GOAL_VALUE = 3 # value determine the vicotry team
    MAX_GAME_DURATION = 128  # seconds
    SCALE = 1
    WINDOW_LENGTH = 1080
    WINDOW_WIDTH = 720
    TARGET_FPS = 64
    TOTAL_FRAMES = MAX_GAME_DURATION * TARGET_FPS
    def __init__(self,observation_mode = 'data'):
        self.action_space = spaces.Box(low=-1,
                                    high=1,  shape=(2,),
                                    dtype=np.float32)
        
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
            self.observation_space = spaces.Box(low=-10000,
                                    high=-10000,
                                    shape=(12,),
                                    dtype=np.float32)
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

        pygame.display.set_caption("Soccer game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.number_allowable_time_second = self.MAX_GAME_DURATION
        self.last_ball_goal_dist = self.field.length/2
        self.did_kicked_ball = False
        self.last_scores = [0,0]
        self.time_since_last_kicked = 0

        # model_path = 'thisisatestmodel' 
        # self.model = PPO.load(model_path)
        # self.model.env = self
        self.screen = None

    def step(self, action, player_index=0):
        default_player = self.players[player_index]
        ball = None
        if len(self.balls) >0:
            ball = self.balls[0]
        dx, dy = action
        dt = 1 / self.TARGET_FPS
        self.number_allowable_time_second -= dt

        last_x, last_y = default_player.x, default_player.y
        # old_player_ball_dist = math.dist([last_x, last_y],
        #                             # [ball.x, ball.y])
        default_player.update(self, dt, dx, dy)
        player_ball_dist = math.dist([default_player.x, default_player.y],
                                    [ball.x, ball.y])
        if default_player.team.is_on_left_side:
            player_team = self.team_a
            opponent_team = self.team_b
            opponent_goal_x, opponent_goal_y_start, opponent_goal_y_end = self.field.right_goal_pos
        else:
            opponent_goal_x, opponent_goal_y_start, opponent_goal_y_end = self.field.left_goal_pos
            player_team = self.team_b
            opponent_team = self.team_a

        if ball.y< opponent_goal_y_start + ball.radius:
            target_y = self.field.goal_y_start + ball.radius
        elif  ball.y> opponent_goal_y_end - ball.radius:
            target_y =   opponent_goal_y_end - ball.radius
        else:
            target_y =   (opponent_goal_y_end +opponent_goal_y_start)/2
       

        ball_goal_dist = math.dist([opponent_goal_x, target_y],
                                [ball.x, ball.y])

        reward = (
            ( - (player_ball_dist + ball_goal_dist) / self.field.length)+
            (-0.1 * (self.time_since_last_kicked / self.MAX_GAME_DURATION))   
        ) / self.TOTAL_FRAMES
        if default_player.is_kicked_ball:
            reward += 0.1
        if abs(ball.vel_x) > 1:
            self.time_since_last_kicked = 0
            ball_speed = math.hypot(self.balls[0].vel_x, self.balls[0].vel_y)
            reward += (1/(self.TARGET_GOAL_VALUE*3) * self.get_ball_score(default_player,ball)* max(min(ball_speed/default_player.walk_speed,1),0.01))/ self.TOTAL_FRAMES
        else:
            self.time_since_last_kicked += dt

        last_player_team_score = player_team.score
        last_opponent_team_score = opponent_team.score

        # Update ball position
        if len(self.balls) > 0:
            self.balls[0].update(self, dt)


        new_player_team_score = player_team.score
        new_opponent_team_score = opponent_team.score

        if new_player_team_score > last_player_team_score:
            reward += 1/(self.TARGET_GOAL_VALUE) * max(0.5, self.number_allowable_time_second / self.MAX_GAME_DURATION)
        elif new_opponent_team_score > last_opponent_team_score:
            reward -=  1/(self.TARGET_GOAL_VALUE) * max(0.5, (self.MAX_GAME_DURATION - self.number_allowable_time_second) / self.MAX_GAME_DURATION)

        # Winning bonus
        if self.get_winning_team() is not None:
            if self.get_winning_team() == default_player.team:
                reward += 2 * max(0.5, self.number_allowable_time_second / self.MAX_GAME_DURATION)
            else:
                reward -= 2 * max(0.5, (self.MAX_GAME_DURATION - self.number_allowable_time_second) / self.MAX_GAME_DURATION)
        reward = reward *100
        # Observation, done, info
        state = self.render(mode="rgb_array") if self.observation_mode == "visual" else self.get_state(default_player)
        done = self.get_winning_team() is not None or self.number_allowable_time_second <= 0
        info = {
            "player_position": (default_player.x, default_player.y),
            "ball_count": len(self.balls),
            "winning_team": self.get_winning_team()
        }
        return state, reward, done, info

    def render(self, mode="human"):
        team_score_distant = 0
        self.screen.fill(self.field.colour)

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
        self.objects = [self.field]

        self.collidable_objects = [self.balls[0]]

        self.team_a.score = 0
        self.team_b.score =0
        self.teams = [self.team_a, self.team_b]

        self.balls[0].reset_ball_position()
        self.objects.append(self.balls[0])
        self.add_random_players()
        self.running = True
        self.number_allowable_time_second = self.MAX_GAME_DURATION
        self.last_ball_goal_dist = self.field.length/2
        self.did_kicked_ball = False
        self.last_scores = [0,0]
        self.time_since_last_kicked = 0
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
            x=random.randint(int(self.OFF_SET * self.SCALE+self.field.length/3),
                             int(self.field.length*2/3 + self.OFF_SET * self.SCALE)),
            y=random.randint(int(self.OFF_SET * self.SCALE+self.field.width/3),
                             int(self.field.width*2/3 + self.OFF_SET * self.SCALE)),
            team=team,
            acceleration=200 , #float(400 * random.uniform(0.8, 1.1)),
            run_speed=600, #float(600 * random.uniform(0.8, 1.1)),
            walk_speed=300,#float(800 * random.uniform(0.8, 1.1)),
            strength=1, #float(random.uniform(1, 1.9)),
            stamina=3000000, #float(3000000 * random.uniform(1, 1.3)),
            dex=float(random.uniform(1, 1.3)),
            mass=60,#float(60 * random.uniform(0.8, 1.5)),
            is_bot= is_bot,
            window_scale=self.SCALE
                                     )
    # add a random player in pair for each team.
    def add_random_players(self):
        MAX_PER_TEAM = 1
        for i in range(MAX_PER_TEAM):
            # create a player the first player's team is random so the AI can learn for both team
            random_value =  random.randint(1,2)
            player = self.create_random_player(team=self.team_a if random_value==1 else self.team_b,is_bot=True)
            self.add_player(player)
            # player = self.create_random_player(team=self.team_a if random_value==2 else self.team_b,is_bot=True)
            # self.add_player(player)

    def get_reward(self, player) -> float:
        
        # # reward_value =-1
        # ball = self.balls[0]
        # dist_to_ball = math.dist([player.x,player.y],[ball.x,ball.y])
        # reward_value = 0
        # target_goal_y = (self.field.goal_y_end + self.field.goal_y_start)/2
        # if player.team.is_on_left_side:
        #     if player.x > ball.x - (ball.radius + player.radius):
        #         dist_to_ball += dist_to_ball
        #     player_team = self.team_a
        #     opponent_team = self.team_b
        #     target_goal_x = self.field.right_goal_pos[0]
        #     # ball_dir_score = 0.25 if ball.vel_x >0 else 0
        # else:
        #     if player.x < ball.x + (ball.radius + player.radius):
        #         dist_to_ball +=dist_to_ball
        #     player_team = self.team_b
        #     opponent_team = self.team_a
        #     target_goal_x = self.field.left_goal_pos[0]
            # ball_dir_score = 0.25 if ball.vel_x <0 else 0
        # dist_to_goal =  math.dist([target_goal_x,target_goal_y],[ball.x,ball.y])



        # reward_value += (-dist_to_ball - dist_to_goal)/self.field.length 
        # #[-4,0]



        # # reward_value+= ball_dir_score
        # # target_goal_y = (self.field.goal_y_end + self.field.goal_y_start)/2

        # # # # minimize the distant to the ball [-field corbnet+ off sett,0]
        # # k_value = -math.dist([player.x,player.y],[ball.x,ball.y])/2

        # # # minimize the distant to the ball to oppnent goal or maximize the distant to the ball to player goal [-1,0]
        # # k_value -= math.dist([target_goal_x,target_goal_y],[ball.x,ball.y])
        # # k_value = k_value/self.field.length 

        # # if player.is_kicked_ball:
        # #     reward_value += ball_dir_score

        # # k_value += player_team.score-opponent_team.score

        # # k_value = -math.dist([player.x,player.y],[ball.x,ball.y])/self.field.length  
        # # k_value += 1 if player.is_kicked_ball else 0
        # #[-1.5,-0.5]
        # reward_value += (player_team.score-opponent_team.score)
        return  -1  


    def get_state(self, player):
        state = []
        state +=[self.team_a.score,self.team_b.score]
        # Ball info: team_side = 0.0 for ball (neutral)
        each_ball = self.balls[0]
        state +=[0.0, each_ball.x, each_ball.y, each_ball.vel_x, each_ball.vel_y]

        team_value = 1.0 if not player.team.is_on_left_side else -1.0
        state +=[team_value, player.x, player.y, player.vel_x, player.vel_y]

        for each_player in self.players:
            if each_player is not player:
                team_value = 1.0 if not each_player.team.is_on_left_side else -1.0
                state += [team_value, each_player.x, each_player.y, each_player.vel_x, each_player.vel_y]

        state_array = np.array(state, dtype=np.float32)
       
        return state_array

    def get_winning_team(self):
        for team in self.teams:
            if team.score >= self.TARGET_GOAL_VALUE:
                return team
        return None
    
    def get_model_action(self, player):
        env = DummyVecEnv([lambda: self])
        state = self.get_state(player)
        self.model.env =env
        action,_  = self.model.predict(state, deterministic=True)
        return action

    def get_ball_score(self, player, ball):
        reward = 0

        if player.team.is_on_left_side:
            current_team_goal_x, current_team_goal_y_top, current_team_goal_y_bottom = self.field.left_goal_pos
            opponent_team_goal_x, opponent_team_goal_y_top, opponent_team_goal_y_bottom = self.field.right_goal_pos
            opponent_team_goal_x -= ball.radius
            current_team_goal_x += ball.radius
        else:
            current_team_goal_x, current_team_goal_y_top, current_team_goal_y_bottom = self.field.right_goal_pos
            opponent_team_goal_x, opponent_team_goal_y_top, opponent_team_goal_y_bottom = self.field.left_goal_pos
            opponent_team_goal_x += ball.radius
            current_team_goal_x -= ball.radius

        if ball.vel_x == 0:
            return reward  
        
        if (player.team.is_on_left_side and ball.vel_x > 0) or (not player.team.is_on_left_side and ball.vel_x < 0):
            intersect_opponent_goal_y = ball.y + (opponent_team_goal_x - ball.x) * (ball.vel_y / ball.vel_x)
            if opponent_team_goal_y_top + ball.radius < intersect_opponent_goal_y < opponent_team_goal_y_bottom - ball.radius:
                reward = 1

        elif (player.team.is_on_left_side and ball.vel_x < 0) or (not player.team.is_on_left_side and ball.vel_x > 0):
            intersect_own_goal_y = ball.y + (current_team_goal_x - ball.x) * (ball.vel_y / ball.vel_x)
            if current_team_goal_y_top + ball.radius <= intersect_own_goal_y <= current_team_goal_y_bottom - ball.radius:
                reward = -1

        return reward

    # def get_model_action(self, player):
    #     # env = DummyVecEnv([lambda: self])
    #     # state = self.get_state(player)
    #     # self.model.env =env
    #     # action,_  = self.model.predict(state, deterministic=True)
    #     return (random.uniform(-1,1),random.uniform(-1,1))
    def update_model(self, model_path):
        self.model =  PPO.load(model_path)
        self.model.env = self