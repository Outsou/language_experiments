class Message:
    def __init__(self, sender, position_of, x, y):
        self._sender = sender
        self._position_of = position_of
        self._x = x
        self._y = y

    @property
    def sender (self):
        return self._sender

    @property
    def position_of (self):
        return self._position_of

    @property
    def x (self):
        return self._x

    @property
    def y (self):
        return self._y
