# IMPORT GAME
from FootBallGameEnv import FootBallGameEnv
import multiprocessing
from typing import Callable
# IMPORT JOYPAD WRAPPER
from nes_py.wrappers import JoypadSpace

# IMPORT THE FRAME STACKER AND GRAY WAPPER
from gym.wrappers import FrameStack, GrayScaleObservation

# import Vectorization wrapper
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv

from matplotlib import pyplot as plt
import os

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from torch.utils.tensorboard import SummaryWriter
import pygame
from datetime import datetime
CHECKPOINT_DIR = './train'
LOG_DIR ='./logs'



CHECKPOINT_DIR = './train/'
LOG_DIR = './logs/'

class BotAgent:
    def __init__(
        self,
        num_envs: int          = 16,
        total_timesteps: int   = 70_000_000,
        policy: str            = "CnnPolicy",  
        device: str            = "auto"         
    ):
        self.num_envs        = num_envs
        self.total_timesteps = total_timesteps
        self.policy          = policy
        self.device          = device

    def create_game_wrapper(self):
        env = FootBallGameEnv()
        env.run()                            

    def _make_env(self) -> Callable[[], FootBallGameEnv]:
        def _init():
            env = FootBallGameEnv()

            # -- add wrappers here if you use any -------------------
            # env = JoypadSpace(env, SIMPLE_MOVEMENT)
            # env = GrayScaleObservation(env, keep_dim=True)
            # env = FrameStack(env, num_stack=4)

            return env
        return _init

    def train(self):
        # Multiprocessing requirement on Windows
        multiprocessing.set_start_method("spawn", force=True)

        # Build vectorised env (16 subprocesses → 16 game windows)
        env_fns = [self._make_env() for _ in range(self.num_envs)]
        envs    = SubprocVecEnv(env_fns)

        # Initialise PPO
        model = PPO(
            policy          = self.policy,
            env             = envs,
            verbose         = 1,
            tensorboard_log = LOG_DIR,
            device          = self.device,
            batch_size=1024,  
            learning_rate=0.0002, 
            n_steps=4096,
            ent_coef=0.001,
            clip_range=0.2,
            target_kl = 0.05,
        )

        callback = TrainAndLoggingCallback(
            check_freq = 2000,            
            save_path  = CHECKPOINT_DIR,
            log_dir = LOG_DIR
        )

        model.learn(
            total_timesteps = self.total_timesteps,
            callback        = callback
        )

        model.save(os.path.join(CHECKPOINT_DIR, "final_model"))
        envs.close()
    def play(self):
        env = FootBallGameEnv()
        model = PPO.load("F:/ai/SoccerAI/train/best_model_at20250717_082320_ep116000_steps860057616.zip", env=env, device="cpu")
        clock = pygame.time.Clock()
        env.screen =  pygame.display.set_mode(
                (env.field.length + env.OFF_SET * 2 * env.SCALE, env.field.width + env.OFF_SET * 2 * env.SCALE))
        while True:
            obs = env.reset()
            done = False
            ep_reward = 0

            while not done:
                # deterministic=True avoids stochastic exploration
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, done, info = env.step(action)
                ep_reward += reward
                env.render()
                clock.tick(60)

            print(f"Episode finished — total reward: {ep_reward:.2f}")

        
class TrainAndLoggingCallback(BaseCallback):
    def __init__(self, check_freq: int, save_path: str, log_dir: str, verbose: int = 1):
        super().__init__(verbose)
        self.check_freq = check_freq
        self.save_path  = save_path
        self.log_dir    = log_dir
        self.ep_rewards  = [0.0] * 16
        self.ep_counter = 0
        self.avg_ep_reward = 0 
        self.reward_record = []

    def _init_callback(self) -> None:
        os.makedirs(self.save_path, exist_ok=True)

    def _on_step(self) -> bool:
        rewards = self.locals["rewards"]   
        dones = self.locals["dones"]       

        for i in range(len(rewards)):
            self.ep_rewards[i] += rewards[i]

            if dones[i]:
                self.ep_counter += 1
                ep_reward = self.ep_rewards[i]
                self.reward_record .append(ep_reward)
                print(f"[CB] Episode {self.ep_counter} done in env {i} with reward {ep_reward}")

                if self.ep_counter % self.check_freq == 0:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    fname = f"best_model_at{timestamp}_ep{self.ep_counter}_steps{self.num_timesteps}"
                    path = os.path.join(self.save_path, fname)
                    self.model.save(path)
                    if self.verbose:
                        print(f"[CB] Saved model to {path}")
                if len(self.reward_record) >= len(rewards):
                    self.logger.record("rollout/ep_reward", sum(self.reward_record)/len(self.reward_record))
                    self.reward_record = []

                self.ep_rewards[i] = 0.0

        return True
    
if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)

    agent = BotAgent(
        num_envs        = 16,        
        total_timesteps = 1000000000, 
        policy          = "MlpPolicy",
        device          = "cpu"       # choose "cpu" to silence GPU warning
    )
    agent.play()
    # avg -22.3k