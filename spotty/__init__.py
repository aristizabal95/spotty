from gymnasium.envs.registration import register
from .env import SpottyEnv

register(
    id="Spotty-v0",
    entrypoint="spotty.env:SpottyEnv",
    nondeterministic=True
)