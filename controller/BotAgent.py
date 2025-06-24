# IMPORT GAME
from testing import World

# IMPORT JOYPAD WRAPPER
from nes_py.wrappers import JoypadSpace

# IMPORT THE FRAME STACKER AND GRAY WAPPER
from gym.wrappers import FrameStack, GrayScaleObservation

# import Vectorization wrapper
from stable_baselines3.common.vec_env import VecFrameStack, DummyVecEnv

from matplotlib import pyplot as plt
import os

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

CHECKPOINT_DIR = './train/'
LOG_DIR = './logs/'

class BotAgent:
    def create_game_wrapper(self):
        env = World()
        env.run()
        # env.reset()
        # state, reward, done, info = env.step([env.action_space.sample()])
        # env = GrayScaleObservation(env,keep_dim=True)
        # # 4. Wrap inside the Dummy Environment
        # env = DummyVecEnv([lambda: env])
        # # 5. Stack the frames
        # env = VecFrameStack(env, 4, channels_order='last')
        # callback = TrainAndLoggingCallback(check_freq=10000, save_path=CHECKPOINT_DIR)
        # model = PPO('CnnPolicy', env, verbose=1, learning_rate=0.000001,
        #             n_steps=512)
        # model.learn(total_timesteps=10001, callback=callback)


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
batagen.create_game_wrapper()