# IMPORT GAME
import sys
sys.path.append(r"F:\ai\SoccerAI")
from FootBallGameEnv import FootBallGameEnv

# IMPORT JOYPAD WRAPPER
from nes_py.wrappers import JoypadSpace

# IMPORT THE FRAME STACKER AND GRAY WAPPER
from gym.wrappers import FrameStack, GrayScaleObservation

# import Vectorization wrapper
from stable_baselines3.common.vec_env import VecFrameStack, DummyVecEnv, SubprocVecEnv
from functools import partial
import datetime
from matplotlib import pyplot as plt
import os

from stable_baselines3 import PPO,DQN
from stable_baselines3.common.callbacks import BaseCallback
import numpy as np
import time      # only needed if you prefer time.sleep()
import pygame
CHECKPOINT_DIR = './train'
LOG_DIR ='./logs'


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

CHECKPOINT_DIR = './train1/'
LOG_DIR = './logs/'
def constant_schedule(_):
    return 0.0003
class BotAgent:
    def train(self):
        # env = FootBallGameEnv()

        # env = DummyVecEnv([lambda: env])

        # callback = TrainAndSaveCallBack(check_feq=save_array, save_path=CHECKPOINT_DIR)
        # # model = DQN('MlpPolicy', env,verbose=1, tensorboard_log=LOG_DIR)
        # model = PPO('MlpPolicy', env, verbose=1, clip_range =0.2, learning_rate=constant_schedule, n_epochs=4,tensorboard_log=LOG_DIR,n_steps = 2048, batch_size = 512,ent_coef = 0.001)

        # # model = PPO('CnnPolicy', env, verbose=1,  learning_rate=0.00001, n_steps=512,ent_coef = 0.01)

        # #start learning model
        def make_env():
            return FootBallGameEnv()
        def constant_schedule(_):
            return 0.0003
        
        env_fns = [make_env for _ in range(8)]        
        env = SubprocVecEnv(env_fns)
        save_array =[50,100,1000,5000,10000,20000,50000,70000,100000,200000,300000,500000,800000,1000000,1200000,1500000,1700000,2000000,2500000,3000000,3600000,4500000,6000000,8000000,10000000,12000000,14000000,16000000,18000000]

        model = PPO('MlpPolicy', env, verbose=1, clip_range =0.3, learning_rate=constant_schedule, n_epochs=6,tensorboard_log=LOG_DIR,n_steps = 4096, batch_size = 512,ent_coef = 0.001)
        callback = TrainAndSaveCallBack(check_feq=save_array, save_path=CHECKPOINT_DIR)
        model.learn(total_timesteps=600000000000,callback=callback)
        model.save('thisisatestmodel')
        env.env_method("update_model", 'thisisatestmodel')


    def train_vs_bot(self, total_timesteps: int = 600000000000, chunk: int = 7372800000, n_envs: int = 16):
        def make_env():
            return FootBallGameEnv()
        def constant_schedule(_):
            return 0.0003
        
        env_fns = [make_env for _ in range(n_envs)]        
        env = SubprocVecEnv(env_fns)
        ##n_steps = 4096, batch_size = 64, clip_range =0.2,n_epochs=10,
        model = PPO('MlpPolicy', env, verbose=1, learning_rate=constant_schedule, tensorboard_log=LOG_DIR, ent_coef = 0.001,batch_size = 128,target_kl = 0.3)
        save_array = [1000000 * i for i in range(1, 50)]
        callback = TrainAndSaveCallBack(check_feq=save_array, save_path=CHECKPOINT_DIR)
        steps_done = 0
        while steps_done < total_timesteps:
            model.learn(total_timesteps=chunk,callback=callback)
            steps_done += chunk
            model.save('thisisatestmodel')
            env.env_method("update_model", 'thisisatestmodel')


        model.save(os.path.join(CHECKPOINT_DIR, "final_model"))
    
    def play(self):
        env = FootBallGameEnv()
        env = DummyVecEnv([lambda: env])
        model_path = 'train1/best_model20250703_143646.zip' 
        model = PPO.load(model_path)
        state = env.reset()
        clock = pygame.time.Clock()                  
        done = False
        while not done:
            action, _ = model.predict(state, deterministic=True)

            state, reward, done, info = env.step(action)
            # Render the base env (not the VecEnv wrapper)
            env.envs[0].render()
                
            for event in pygame.event.get():  
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            clock.tick(60)   
            if done:
                done = False
                env.reset()
    
    def manual(self):
          env = World()
          env.run()
    def con_train(self):
        env = FootBallGameEnv()
        # env = GrayScaleObservation(env,keep_dim=True)
        # 4. Wrap inside the Dummy Environment
        env = DummyVecEnv([lambda: env])
        env = VecFrameStack(env, 3, channels_order='last')

        # 5. Stack the frames
        callback = TrainAndSaveCallBack(check_feq=[900 * 2**i for i in range(30)], save_path=CHECKPOINT_DIR)
        # model = DQN('MlpPolicy', env,verbose=1, tensorboard_log=LOG_DIR)

        model_path = 'train1/best_model1700000.zip' 
        model = PPO.load(model_path)
        model.env = env
        # model = PPO('CnnPolicy', env, verbose=1,  learning_rate=0.00001, n_steps=512,ent_coef = 0.01)

        #start learning model
        model.learn(total_timesteps=80000000,callback=callback)
        model.save('thisisatestmodel')

class TrainAndSaveCallBack(BaseCallback):
    def __init__(self,check_feq,save_path,verbose =1):
        super(TrainAndSaveCallBack,self).__init__(verbose)
        self.check_feq = check_feq
        self.save_path = save_path
        self.episode_rewards = []
        self.current_rewards = []
        self.count = 0
        self.highest_reward = -float('inf')
    def _init_callback(self) -> None:
        if self.save_path is not None:
            os.makedirs(self.save_path,exist_ok=True)
    def _on_step(self) -> bool:
        # Accumulate rewards for current episode
        reward = self.locals["rewards"][0]
        self.current_rewards.append(reward)

        # Check if episode ended
        done = self.locals["dones"][0]
        if done:
            episode_reward = np.sum(self.current_rewards)
            self.episode_rewards.append(episode_reward)
            self.current_rewards = []

            # Log the raw episode reward directly to TensorBoard
            self.logger.record("custom/episode_reward", episode_reward)

        # Save model if at checkpoint
        if self.count< len(self.check_feq) and self.n_calls>= self.check_feq[self.count]:
            self.count +=1
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            path = os.path.join(self.save_path, f'best_model{timestamp}')
            self.model.save(path)
        return True

if __name__ == "__main__":
    batagen= BotAgent()
    # batagen.play()
    batagen.train_vs_bot()
