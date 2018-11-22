# server.py
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from coopa_model import CoopaModel
from mesa.visualization.UserParam import UserSettableParameter
from ui_styling import agent_portrayal, PORTRAYALS, AGENT_TYPES
from layout import Layout

# Reverse to sorted keys to get coopa as the default agent as we are currently building it.
agent_type = UserSettableParameter('choice', 'Agent type', value=sorted(AGENT_TYPES.keys(), reverse=True)[0],
                                   choices=sorted(AGENT_TYPES.keys()))

w, h = Layout.width, Layout.height
grid = CanvasGrid(agent_portrayal, w, h, 20 * w, 20 * h)

def get_server(play_guessing):
    server = ModularServer(CoopaModel,
                           [grid],
                           "Coopa Model",
                           {"play_guessing": play_guessing})
    return server
