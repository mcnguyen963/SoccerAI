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
    MAX_GAME_DURATION = 120  # seconds
    SCALE = 1
    WINDOW_LENGTH = 1080
    WINDOW_WIDTH = 720
    TARGET_FPS = 64
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
        self.screen = pygame.display.set_mode(
            (self.field.length + self.OFF_SET * 2 * self.SCALE, self.field.width + self.OFF_SET * 2 * self.SCALE))
        pygame.display.set_caption("Soccer game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.number_allowable_time_second = self.MAX_GAME_DURATION
        self.last_ball_dist = float('inf')
        self.last_ball_goal_dist = self.field.length/2
        model_path = 'thisisatestmodel' 
        self.model = PPO.load(model_path)
        self.model.env = self

    def step(self, action,  player_index = 0):
        default_player = self.players[player_index]
        dt = 1/self.TARGET_FPS
        self.number_allowable_time_second -= dt
        dx, dy = action[0], action[1]
        self.last_ball_dist = math.dist([default_player.x,default_player.y],[self.balls[0].x,self.balls[0].y])
        if default_player.team.is_on_left_side:
            player_last_score = self.team_a.score
            opponent_last_score = self.team_b.score
        else:
            player_last_score = self.team_b.score
            opponent_last_score = self.team_a.score

        default_player.update(self, dt, dx, dy)
        reward = self.get_reward(default_player)

        if default_player.team.is_on_left_side:
            player_new_score = self.team_a.score
            opponent_new_score = self.team_b.score
            target_goal_x = self.field.right_goal_pos[0]
        else:
            player_new_score = self.team_b.score
            opponent_new_score = self.team_a.score
            target_goal_x = self.field.left_goal_pos[0]
        target_goal_y = (self.field.goal_y_end+self.field.goal_y_end)/2
        self.last_ball_goal_dist = math.dist([target_goal_x,target_goal_y],[self.balls[0].x,self.balls[0].y])

        if len(self.balls)>0:
            self.balls[0].update(self,dt)
        current_ball_goal_dist =  math.dist([target_goal_x,target_goal_y],[self.balls[0].x,self.balls[0].y])
        if current_ball_goal_dist< self.last_ball_goal_dist:
            reward +=1
        elif current_ball_goal_dist> self.last_ball_goal_dist:
            reward -=1

        total_frame = self.TARGET_FPS*self.number_allowable_time_second

        if default_player.is_kicked_ball:
            if default_player.team.is_on_left_side and default_player.x <self.balls[0].x or not default_player.team.is_on_left_side and default_player.x >self.balls[0].x:
                reward += self.TARGET_FPS * 5
            if self.balls[0].vel_x >0 and default_player.team.is_on_left_side:
                reward += self.TARGET_FPS
            elif self.balls[0].vel_x <0 and not default_player.team.is_on_left_side:
                reward += self.TARGET_FPS

        if player_new_score>player_last_score:
            reward += max(total_frame/self.TARGET_GOAL_VALUE,3)
            
        if opponent_new_score>opponent_last_score:
            x = self.TARGET_FPS*(self.MAX_GAME_DURATION-self.number_allowable_time_second)
            reward -= max(x/self.TARGET_GOAL_VALUE,3)

        # for each other aciton/
        # update them
        # player2 = self.players[1]
        # # dx,dy = self.get_model_action(player2)
        # player2.update(self,dt,random.uniform(-1,1),random.uniform(-1,1))


        # Compute reward and check for terminal condition

        # self.player_controller.bot_controller(dt,player2)

        if self.observation_mode == "visual":
            state = self.render(mode="rgb_array")  # H×W×3 frame
        else:
            state = self.get_state(default_player)

        done = self.get_winning_team() is not None or self.number_allowable_time_second <= 0

        info = {
            "player_position": (default_player.x, default_player.y),
            "ball_count": len(self.balls),
            "winning_team": self.get_winning_team()
        }
        if self.get_winning_team() is not None:
            if self.get_winning_team == default_player.team:
                reward += max(total_frame,10)
            else:
                reward -= max(total_frame,10)

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
        self.last_ball_dist =  math.dist([self.balls[0].x,self.balls[0].y],[ self.players[0].x, self.players[0].y])
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
            acceleration=400 , #float(400 * random.uniform(0.8, 1.1)),
            run_speed=600, #float(600 * random.uniform(0.8, 1.1)),
            walk_speed=800,#float(800 * random.uniform(0.8, 1.1)),
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
        reward_value =-1
        ball = self.balls[0]
        current_distant = math.dist([player.x,player.y],[ball.x,ball.y])
        if self.last_ball_dist-current_distant<-2:
            reward_value+=0.5
        elif self.last_ball_dist-current_distant>2:
            reward_value-=0.5
        else:
            reward_value-=1
    
        # if player.team.is_on_left_side:
        #     # player_team = self.team_a
        #     # opponent_team = self.team_b
        #     ball_dir_score = 0.25 if ball.vel_x >0 else 0
        #     # target_goal_x = self.field.right_goal_pos[0]
        # else:
        #     # player_team = self.team_b
        #     # opponent_team = self.team_a
        #     # target_goal_x = self.field.left_goal_pos[0]
        #     ball_dir_score = 0.25 if ball.vel_x <0 else 0

        # reward_value+= ball_dir_score
        # target_goal_y = (self.field.goal_y_end + self.field.goal_y_start)/2

        # # # minimize the distant to the ball [-field corbnet+ off sett,0]
        # k_value = -math.dist([player.x,player.y],[ball.x,ball.y])/2

        # # minimize the distant to the ball to oppnent goal or maximize the distant to the ball to player goal [-1,0]
        # k_value -= math.dist([target_goal_x,target_goal_y],[ball.x,ball.y])
        # k_value = k_value/self.field.length 

        # if player.is_kicked_ball:
        #     reward_value += ball_dir_score

        # k_value += player_team.score-opponent_team.score

        # k_value = -math.dist([player.x,player.y],[ball.x,ball.y])/self.field.length  
        # k_value += 1 if player.is_kicked_ball else 0
        # k_value = (player_team.score-opponent_team.score)
        #[-1.5,-0.5]
        return  reward_value  


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
        
    # def get_model_action(self, player):
    #     # env = DummyVecEnv([lambda: self])
    #     # state = self.get_state(player)
    #     # self.model.env =env
    #     # action,_  = self.model.predict(state, deterministic=True)
    #     return (random.uniform(-1,1),random.uniform(-1,1))
    def update_model(self, model_path):
        self.model =  PPO.load(model_path)
        self.model.env = self