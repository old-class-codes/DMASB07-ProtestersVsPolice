import random

from mesa import Agent


class Cop(Agent):
    """
    A cop for life.  No defection.
    Summary of rule: Inspect local vision and arrest a random active agent.

    Attributes:
        unique_id: unique int
        x, y: Grid coordinates
        vision: number of cells in each direction (N, S, E and W) that cop is
            able to inspect
    """

    def __init__(self, unique_id, model, pos, vision):
        """
        Create a new Cop.
        Args:
            unique_id: unique int
            x, y: Grid coordinates
            vision: number of cells in each direction (N, S, E and W) that
                agent can inspect. Exogenous.
            model: model instance
        """
        super().__init__(unique_id, model)
        self.breed = "cop"
        self.pos = pos
        self.vision = vision
        # TODO: see if they can disappear if not then freeze
        # TODO: make cops disappear for awhile when arresting - yes
        # TODO: change colour while arresting and away
        self.arresting = False  # TODO: make cops disappear for awhile when arresting
        self.arrested_step = 0
        self.wait_for = 40  # no of steps to wait before arresting someone else

    def step(self):
        """
        Inspect local vision and arrest a random active agent. Move if
        applicable.
        """
        self.update_neighbors()
        active_neighbors = []
        deviant_neighbors = []
        cop_neighbors = []
        for agent in self.neighbors:
            if agent.breed == "citizen" and agent.condition == "Active" and agent.jail_sentence == 0:
                active_neighbors.append(agent)
            if agent.breed == "cop":
                cop_neighbors.append(agent)
            if agent.breed == "citizen" and agent.condition == "Deviant":
                deviant_neighbors.append(agent)
        # TODO: have multiple cops per person to arrest? try grouping cops together
        # TODO: make it slightly less likely to arrest ? seems too simple rn

        if not self.arresting and (self.model.iteration - self.arrested_step <= self.wait_for):
            self.arresting = True

        if deviant_neighbors and self.model.jail_capacity > len(self.model.jailed_agents):
            arrestee = self.random.choice(deviant_neighbors)
            sentence = self.random.randint(0, self.model.max_jail_term)
            arrestee.jail_sentence = sentence
            self.model.jailed += 1
            self.model.arrested_agents.append(arrestee)
            self.arresting = False
            self.arrested_step = self.model.iteration
        elif (
            active_neighbors
            and self.model.jail_capacity > len(self.model.jailed_agents)
            and self.arresting and len(cop_neighbors) > 1
        ):  # TODO : check this once
            arrestee = self.random.choice(active_neighbors)
            sentence = self.random.randint(0, self.model.max_jail_term)
            arrestee.jail_sentence = sentence
            self.model.jailed += 1
            self.model.arrested_agents.append(arrestee)
            self.arresting = False
            self.arrested_step = self.model.iteration

        if self.model.movement and self.empty_neighbors:
            useful_move = self.move_towards_actives()
            if useful_move:
                self.model.grid.move_agent(self, useful_move)
            else:
                self.model.grid.move_agent(self, self.random.choice(self.empty_neighbors))

    def move_towards_actives(self):
        neighborhood = self.model.grid.get_neighborhood(self.pos, moore=False, radius=self.vision)
        deviants, actives = [], []
        toward = None
        for x in neighborhood:
            neighbor = self.model.grid.get_cell_list_contents(x)
            if neighbor and neighbor[0].breed == "citizen":
                if neighbor[0].condition == "Deviant":
                    deviants.append(x)
                if neighbor[0].condition == "Active":
                    actives.append(x)
        if deviants:
            toward = random.choice(deviants)
        elif actives:
            toward = random.choice(actives)
        else:
            return None
        dict = {"left": (self.pos[0]-1, self.pos[1]), "right": (self.pos[0]+1, self.pos[1]),
                "up": (self.pos[0], self.pos[1]-1), "down": (self.pos[0], self.pos[1]+1)}
        new_pos = []
        if toward:
            if toward[0] > self.pos[0]:  # citizen is more right than cop
                new_pos.append("right")
            elif toward[0] < self.pos[0]:  # citizen is more left than cop
                new_pos.append("left")
            if toward[1] > self.pos[1]:  # citizen is further down than cop
                new_pos.append("down")
            elif toward[1] < self.pos[1]:  # citizen is further up than cop
                new_pos.append("up")
        new_pos = dict[random.choice(new_pos)]
        return new_pos

    def update_neighbors(self):
        """
        Look around and see who my neighbors are.
        """
        self.neighborhood = self.model.grid.get_neighborhood(
            self.pos, moore=False, radius=1
        )
        self.neighbors = self.model.grid.get_cell_list_contents(self.neighborhood)
        self.empty_neighbors = [
            c for c in self.neighborhood if self.model.grid.is_cell_empty(c)
        ]


