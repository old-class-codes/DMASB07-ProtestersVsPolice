import argparse
import re

from mesa.batchrunner import BatchRunner
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter

from .agents.block import Block
from .agents.citizen import Citizen
from .agents.cop import Cop
from .model import ProtestersVsPolice

# ap = argparse.ArgumentParser("Protesters Vs Police")
# ap.add_argument("-b", action='store_true',help="Batch runner")
# ags = ap.parse_args()

COP_COLOR = "#000000"
COP_ARRESTING_COLOR = "#fcba03"
AGENT_QUIET_COLOR = "#0066CC"
AGENT_REBEL_COLOR = "#CC0000"
AGENT_DEVIANT_COLOR = "#00FBFF"
JAIL_COLOR = "#757575"
BARRICADE_COLOR = "#00FF00"


def citizen_cop_portrayal(agent):
    if agent is None:
        return

    portrayal = {
        "Shape": "circle",
        "x": agent.pos[0],
        "y": agent.pos[1],
        "Filled": "true",
    }

    if type(agent) is Citizen:
        color = (
            AGENT_QUIET_COLOR if agent.condition == "Quiescent" else AGENT_REBEL_COLOR
        )
        color = AGENT_DEVIANT_COLOR if agent.condition == "Deviant" else color
        color = JAIL_COLOR if agent.jail_sentence else color
        portrayal["Color"] = color
        portrayal["r"] = 0.8
        portrayal["Layer"] = 0

    elif type(agent) is Block:
        portrayal["Shape"] = "rect"
        portrayal["Color"] = BARRICADE_COLOR
        portrayal["h"] = 0.9
        portrayal["w"] = 0.9
        portrayal["Layer"] = 0

    elif type(agent) is Cop:
        color = COP_COLOR if agent.can_arrest else COP_ARRESTING_COLOR
        portrayal["Color"] = color
        portrayal["r"] = 0.5
        portrayal["Layer"] = 1
    return portrayal


model_params = {
    "grid_density": UserSettableParameter(
        param_type="slider",
        name="Grid density",
        value=0.8,
        min_value=0,
        max_value=1,
        step=0.01,
        description="",
    ),
    "ratio": UserSettableParameter(
        param_type="slider",
        name="Citizen to cop ratio",
        value=0.8,
        min_value=0,
        max_value=1,
        step=0.001,
        description="",
    ),
    "jail_capacity": UserSettableParameter(
        param_type="slider",
        name="Jail capacity",
        value=50,
        min_value=0,
        max_value=1550,
        step=1,
        description="",
    ),
    "environment": UserSettableParameter(
        param_type="choice",
        name="Environment",
        value="Random distribution",
        choices=[
            "Random distribution",
            "Block in the middle",
            "Cops in the middle",
            "Wall of cops",
            "Street",
        ],
        description="",
    ),
    "wrap": UserSettableParameter(
        param_type="choice",
        name="Wrap",
        value="Don't wrap around",
        choices=["Wrap around", "Don't wrap around"],
        description="",
    ),
    "direction_bias": UserSettableParameter(
        param_type="choice",
        name="Citizen Direction",
        value="Random",
        choices=[
            "Random",
            "Clockwise",
            "Anti-clockwise",
            "left",
            "right",
            "up",
            "down",
        ],
        description="",
    ),
    "height": 40,
    "width": 40,
    "citizen_vision": 7,
    "cop_vision": 7,
    "barricade": 50,
    "funmode": False,  # Set to True for sound effects
}


class AgentLeftElement(TextElement):
    """
    Display a text count of how many agents there are.
    """

    def __init__(self):
        pass

    def render(self, model):
        cop = 0
        citizen = 0
        block = 0
        for agent in model.schedule.agents:
            if agent.breed == "citizen":
                citizen += 1
            if agent.breed == "cop":
                cop += 1
            if agent.breed == "Block":
                block += 1

        stats = f"""Number of citizens: {str(citizen)}, Number of jailed citizens: {str(len(model.jailed_agents))}, \n Number of cops: {str(cop)}, Number of blocks: {str(block)}, \n Average Aggression: {model.avg_agg}"""  # FIXME New lines somehow don't work?
        return stats


chart = ChartModule(
    [
        {"Label": "Quiescent", "Color": AGENT_QUIET_COLOR},
        {"Label": "Active", "Color": AGENT_REBEL_COLOR},
        {"Label": "Jailed", "Color": JAIL_COLOR},
        {"Label": "Deviant", "Color": AGENT_DEVIANT_COLOR},
    ],
    data_collector_name="datacollector",
)

# def batch_run(model):
# print(ags.b)
# if ags.b == True:
#     pass
# else:
canvas_element = CanvasGrid(citizen_cop_portrayal, 40, 40, 480, 480)
server = ModularServer(
    ProtestersVsPolice,
    [canvas_element, AgentLeftElement(), chart],
    "Protesters vs Police",
    model_params,
)
