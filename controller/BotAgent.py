# IMPORT GAME
from FootBallGameEnv import FootBallGameEnv

# IMPORT JOYPAD WRAPPER
from nes_py.wrappers import JoypadSpace

# IMPORT THE FRAME STACKER AND GRAY WAPPER
from gym.wrappers import FrameStack, GrayScaleObservation

# import Vectorization wrapper
from stable_baselines3.common.vec_env import VecFrameStack, DummyVecEnv

from matplotlib import pyplot as plt
import os
import numpy as np

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback

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

CHECKPOINT_DIR = '/Volumes/Untitled/xoa/aidatalog/train/'
LOG_DIR = '/Volumes/Untitled/xoa/aidatalog/logs'

class BotAgent:
    def train(self):
        env = FootBallGameEnv()
        # 4. Wrap inside the Dummy Environment
        # env = DummyVecEnv([lambda: env])
        # 5. Stack the frames
        model = PPO('MlpPolicy', env, verbose=1, tensorboard_log=LOG_DIR, learning_rate=0.000001,
                    n_steps=640)

        #
        model.learn(total_timesteps=500000)


class TrainAndLoggingCallback(BaseCallback):

    def __init__(self, check_freq, save_path, verbose=1):
        super(TrainAndLoggingCallback, self).__init__(verbose)
        self.check_freq = check_freq
        self.save_path = save_path

    def _init_callback(self):
        if self.save_path is not None:
            os.makedirs(self.save_path, exist_ok=True)

    def _on_step(self):
        if self.n_calls % self.check_freq == 0:
            model_path = os.path.join(self.save_path, 'best_model_{}'.format(self.n_calls))
            self.model.save(model_path)

        return True
batagen= BotAgent()
batagen.train()