"""Altered priority queue implementation from: https://docs.python.org/3/library/heapq.html

"""
from heapq import *
import itertools


class PQ:
    """Priority queue implementation using heapq.
    """
    def __init__(self):
        self.pq = []                         # list of entries arranged in a heap
        self.entry_finder = {}               # mapping of tasks to entries
        self.REMOVED = '<removed-task>'      # placeholder for a removed task
        self.counter = itertools.count()     # unique sequence count

    def add_task(self, task, priority=0, update_only_lower=True):
        """Add a new task or update the priority of an existing task.
        """
        if task in self.entry_finder:
            # If priority would not diminish, do nothing
            if update_only_lower is True and self.entry_finder[task][0] <= priority:
                return
            self.remove_task(task)
        count = next(self.counter)
        entry = [priority, count, task]
        self.entry_finder[task] = entry
        heappush(self.pq, entry)

    def remove_task(self, task):
        """Mark an existing task as REMOVED.  Raise KeyError if not found.
        """
        entry = self.entry_finder.pop(task)
        entry[-1] = self.REMOVED

    def pop_task(self):
        """Remove and return the lowest priority task. Raise KeyError if empty.
        """
        while self.pq:
            priority, count, task = heappop(self.pq)
            if task is not self.REMOVED:
                del self.entry_finder[task]
                return task
        raise KeyError('pop from an empty priority queue')