from agent import AgentBasic
from objects import Wall
from objects import Resource, DropPoint


PORTRAYALS = {
    AgentBasic: {
        "Color": "green",
        "Layer": 0,
        "scale": 0.8,
        "heading_x": 1,
        "heading_y": 1,
        "Shape": "arrowHead"
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
        if key == 'heading_x':
            try:
                heading_x = agent.heading_x
                portrayal[key] = heading_x
            except AttributeError:
                pass
        if key == 'heading_y':
            try:
                heading_y = agent.heading_y
                portrayal[key] = heading_y
            except AttributeError:
                pass

    return portrayal
