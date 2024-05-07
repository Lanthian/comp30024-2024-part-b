"""prioritydict.py: Implements a priority dictionary data structure that stores
equal priority items in LIFO queues."""

__author__ = "Liam Anthian"
__credits__ = ["Liam Anthian", "Anthony Hill"] 

# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Single Player Tetress

from queue import LifoQueue


class PriorityDict:
    """
    A data structure that acts like a priority queue where equal priority items 
    have LIFO behaviour. Exists in dictionary form to allow O(1) insertion of
    items as opposed to the O(log(m)) insertion of Queue.PriorityQueue.
    """
    # Class fields - initialised on creation
    items: dict[int, LifoQueue]
    size: int                       # tracks size as operations performed

    def __init__(self):
        self.items = {}
        self.size = 0

    def put(self, priority, item):
        """Adds an item of priority `priority` to a PriorityDict."""
        if priority not in self.items.keys():
            # No items of priority yet, create listing
            self.items[priority] = LifoQueue()
        self.items[priority].put(item)
        self.size += 1
        # PriorityQueue.put(self.items[priority], item)

    def get(self):
        """Returns the smallest item in a PriorityDict."""
        k = list(self.items.keys())
        if len(k) == 0:
            # No items as of current
            return None
        smallest = min(k)
        
        # Otherwise, return smallest item
        t = self.items[smallest].get()
        if self.items[smallest].empty():
            # Delete key in dict if last of given priority
            del self.items[smallest]
        
        self.size -= 1
        return t
    
    def empty(self) -> bool:
        """Returns true if PriorityDict has no items, false otherwise."""
        return len(list(self.items.keys())) == 0
    
    def clear(self):
        """Clears the priority dictionary of all items."""
        self.items.clear()
        self.size = 0
    