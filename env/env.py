from gymnasium import Env, spaces
import yaml
from adafruit_servokit import ServoKit
import board
import busio
import numpy as np

from video_capture import VideoCapture
from sensor_retriever import SensorRetriever


class SpottyEnv(Env):
    def __init__(self, config_path="config.yaml"):
        self.config_path = config_path
        self.i2c_bus0 = busio.I2C(board.SCL_1, board.SDA_1)
        self.kit = ServoKit(channels=16, i2c=self.i2c_bus0)
        self.video = VideoCapture()
        self.sensors = SensorRetriever()
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(12,), dtype=np.float32)
        self.observation_space = spaces.Dict({
            "img": spaces.Box(low=0, high=255, shape=(128, 128, 3), dtype=np.uint8),
            "sensors": spaces.Box(
                low=np.array([-1, -1, -100, -100, -100, -100, -1, -1, -1, -1, -1, -1, -100]),
                high=np.array([1, 1, 100, 100, 100, 100, 1, 1, 1, 1, 1, 1, 100])
            ),
            "servos": self.action_space
        })
        self.__reload()


    def reset(self):
        self.__reload()
        self.position = self.__set_initial_pos()
        observation = self.__get_obs()
        self.prev_observation = observation
        info = self.__get_info()
        return observation, info


    def step(self, action):
        action = np.clip(action, -1, 1)
        self.__set_servos(action)
        self.position = action
        observation = self.__get_obs()
        reward = self.__get_reward(observation, self.prev_observation)
        info = self.__get_info()
        terminated = False
        truncated = False

        return observation, reward, terminated, truncated, info


    def close(self):
        for servo in self.config['servos']:
            self.kit.servo[servo['idx']].angle = None

    
    def __reload(self):
        self.config = self.load()
        self.__set_pwm_range()


    def load(self):
        with open(self.config_path, "r") as f:
            config = yaml.safe_load(f)

        return config


    def __get_obs(self):
        return {
            "img": self.video.read(),
            "sensors": self.sensors(),
            "servos": self.position
        }


    def __get_info(self):
        return {}


    def __get_reward(self, obs, prev_obs):
        sensors = np.array(obs['sensors'])
        prev_sensors = np.array(prev_obs['sensors'])
        current = sensors[12]
        delta_imu = sensors[2:12] - prev_sensors[2:12]
        delta_imu_mag = np.linalg.norm(delta_imu)
        return -current - delta_imu_mag


    def __set_pwm_range(self):
        for servo in self.config['servos']:
            servo_idx = servo['idx']
            pwm_range = servo['pwm_range']
            if pwm_range is not None:
                self.kit.servo[servo_idx].set_pulse_width_range(*pwm_range)

    
    def __set_initial_pos(self):
        vals = self.config['default_pos']
        self.__set_servos(vals)
        return vals
    

    def __set_servos(self, vals):
        act_range = self.config['act_range']
        for i, val in enumerate(vals):
            servo = self.config['servos'][i]
            servo_idx = servo['idx']
            servo_range = servo['range']
            servo_angle = np.interp(val, act_range, servo_range)
            self.kit.servo[servo_idx].angle = servo_angle
