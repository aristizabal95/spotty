import io
import base64
import gymnasium as gym
from gymnasium import Env
import numpy as np
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import json
import threading
import time
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

class DashEnvironmentWrapper(Env):
    def __init__(self, env_name, max_length=1000, host='127.0.0.1', port=8050, update_interval=1000):
        self.env = gym.make(env_name)
        self.observation_space = self.env.observation_space
        self.action_space = self.env.action_space
        
        self.max_length = max_length
        self.sensor_data = {f'sensor_{i}': [] for i in range(self.observation_space['sensors'].shape[0])}
        self.servo_data = {f'servo_{i}': [] for i in range(self.observation_space['servos'].shape[0])}
        self.reward_data = []
        self.img = None
        
        self.host = host
        self.port = port
        self.update_interval = update_interval
        
        self.app = dash.Dash(__name__, update_title=None)
        self.setup_dash_app()
        
        self.server_thread = threading.Thread(target=self.run_server, daemon=True)
        self.server_thread.start()

    def setup_dash_app(self):
        sensors_initial_data = [{
            'x': [],
            'y': [],
            'name': f'Sensor {i}'
        } for i in range(self.observation_space['sensors'].shape[0])]
        servos_initial_data = [{
            'x': [],
            'y': [],
            'name': f'Servo {i}'
        } for i in range(self.observation_space['servos'].shape[0])]

        self.app.layout = html.Div([
            html.H1(children='Spotty Environment'),
            html.Div(children=[
                dcc.Graph(id='live-graph', 
                        figure={'data': sensors_initial_data, 
                                'layout': {'uirevision': 'constant',
                                            'title': "Sensors",
                                            'xaxis': {'title': 'Time'},
                                            'yaxis': {'title': 'Sensor Values'}}}),
                html.Img(id='live-image', src=''),
                dcc.Graph(id='live-servos-graph',
                        figure={'data': servos_initial_data, 
                                'layout': {'uirevision': 'constant',
                                            'title': 'Servos Values',
                                            'xaxis': {'title': 'Time'},
                                            'yaxis': {'title': 'Servos Values'}}}),
                dcc.Graph(id='live-reward-graph',
                        figure={'data': [{'x': [], 'y': []}], 
                                'layout': {'uirevision': 'constant',
                                            'title': 'Reward',
                                            'xaxis': {'title': 'Time'},
                                            'yaxis': {'title': 'Servos Values'}}}),
            ]),
            dcc.Store(id='offset', data=0),
            dcc.Interval(id='store-updater', interval=self.update_interval)
        ])


        @self.app.callback(Output('live-graph', 'figure'), Input('store-updater', 'n_intervals'))
        def update_graph(n):
            traces = []
            for name, vals in self.sensor_data.items():
                traces.append({
                    'x': list(range(len(vals))),
                    'y': vals,
                    'name': name
                })
            return {'data': traces}

        @self.app.callback(Output('live-servos-graph', 'figure'), Input('store-updater', 'n_intervals'))
        def update_servos_graph(n):
            traces = []
            for name, vals in self.servo_data.items():
                traces.append({
                    'x': list(range(len(vals))),
                    'y': vals,
                    'name': name
                })
            return {'data': traces}

        @self.app.callback(Output('live-reward-graph', 'figure'), Input('store-updater', 'n_intervals'))
        def update_reward_graph(n):
            traces = []
            traces.append({
                'x': list(range(len(self.reward_data))),
                'y': self.reward_data,
            })
            return {'data': traces}

        @self.app.callback(Output('live-image', 'src'), Input('store-updater', 'n_intervals'))
        def update_img(n):
            return self.capture_image()

    def capture_image(self):
        if self.img is not None:
            # Convert the image from BGR to RGB
            img = Image.fromarray(self.img)
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG")
            encoded_image = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/jpeg;base64,{encoded_image}"
        return ""
    

    def run_server(self):
        self.app.run_server(debug=True, use_reloader=False, host=self.host, port=self.port)

    def step(self, action):
        observation, reward, done, truncated, info = self.env.step(action)
        
        for i, value in enumerate(observation['sensors']):
            self.sensor_data[f'sensor_{i}'].append(float(value))
            if len(self.sensor_data[f'sensor_{i}']) > self.max_length:
                self.sensor_data[f'sensor_{i}'] = self.sensor_data[f'sensor_{i}'][-self.max_length:]

        for i, value in enumerate(observation['servos']):
            self.servo_data[f'servo_{i}'].append(float(value))
            if len(self.servo_data[f'servo_{i}']) > self.max_length:
                self.servo_data[f'servo_{i}'] = self.servo_data[f'servo_{i}'][-self.max_length:]

        self.reward_data.append(reward)
        if len(self.reward_data) > self.max_length:
            self.reward_data = self.reward_data[-self.max_length:]

        self.img = observation['img']

        
        return observation, reward, done, truncated, info

    def reset(self, **kwargs):
        observation, info = self.env.reset(**kwargs)
        
        self.current_time = 0
        self.time_data = [self.current_time]
        for i, value in enumerate(observation['sensors']):
            self.sensor_data[f'sensor_{i}'] = [float(value)]
        for i, value in enumerate(observation['servos']):
            self.servo_data[f'servo_{i}'] = [float(value)]

        self.img = observation['img']
        
        return observation, info

    def render(self):
        return self.env.render()

    def close(self):
        self.env.close()

# Usage
if __name__ == "__main__":
    env = DashEnvironmentWrapper("Spotty-v0", 
                                 max_length=1000,
                                 host='0.0.0.0',
                                 port=8050,
                                 update_interval=500)  # Update store every 1000ms

    try:
        while True:
            observation, _ = env.reset()
            done = False
            while not done:
                # action = env.action_space.sample()
                action = np.array(observation['servos'])
                action = action + np.random.normal(scale=0.01, size=action.shape)
                observation, reward, done, truncated, info = env.step(action)
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        env.close()