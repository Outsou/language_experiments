class MessageDispatcher:

    def __init__(self):
        self._agents = []

    def broadcast(self, message):
        print('-- Broad casting for agent# {}'.format(message.sender.unique_id))
        for agent in self._agents:
            if agent is not message.sender:
                agent.receive(message)

    def register(self, agent):
        self._agents.append(agent)

    def unregister(self, agent):
        self._agents.remove(agent)
