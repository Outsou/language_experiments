# server.py
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from coopa_model import CoopaModel
from mesa.visualization.UserParam import UserSettableParameter
from ui_styling import agent_portrayal, PORTRAYALS, AGENT_TYPES
from layout import get_env_cls

# Reverse to sorted keys to get coopa as the default agent as we are currently building it.
agent_type = UserSettableParameter('choice', 'Agent type', value=sorted(AGENT_TYPES.keys(), reverse=True)[0],
                                   choices=sorted(AGENT_TYPES.keys()))

# w, h = Layout.width, Layout.height


def get_server(play_guessing, random_behaviour, env_name):
    env_cls = get_env_cls(env_name)
    grid = CanvasGrid(agent_portrayal, env_cls.width, env_cls.height, 20 * env_cls.width, 20 * env_cls.height)
    server = ModularServer(CoopaModel,
                           [grid],
                           "Coopa Model",
                           {"play_guessing": play_guessing,
                            "random_behaviour": random_behaviour,
                            "env_name": env_name})
    return server
