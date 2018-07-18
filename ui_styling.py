from agent import AgentBasic
from objects import Wall
from objects import Resource, DropPoint


PORTRAYALS = {
    AgentBasic: {
        "Color": "green",
        "Layer": 0,
        "r": 0.8
    },
    Wall: {
        "Color": "grey",
        "Layer": 0,
        "w": 1,
        "h": 1,
        "Shape": "rect"
    },
    Resource: {
        "Color": "red",
        "Layer": 0
    },
    DropPoint: {
        "Color": "green",
        "Layer": 0,
        "w": 1,
        "h": 1,
        "Shape": "rect"
    }
}

AGENT_TYPES = {
    'basic': AgentBasic
}


def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "r": 0.5}

    for key, value in PORTRAYALS[type(agent)].items():
        portrayal[key] = value
        if key == 'Color':
            try:
                color = agent.color
                portrayal[key] = color
            except AttributeError:
                pass

    return portrayal
