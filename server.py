# server.py
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from coopa_model import CoopaModel
from mesa.visualization.UserParam import UserSettableParameter
from ui_styling import agent_portrayal, PORTRAYALS, AGENT_TYPES

# Reverse to sorted keys to get coopa as the default agent as we are currently building it.
agent_type = UserSettableParameter('choice', 'Agent type', value=sorted(AGENT_TYPES.keys(), reverse=True)[0],
                                   choices=sorted(AGENT_TYPES.keys()))

grid = CanvasGrid(agent_portrayal, 10, 18, 200, 360)

server = ModularServer(CoopaModel,
                       [grid],
                       "Coopa Model")
