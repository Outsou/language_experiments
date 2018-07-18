from objects import Wall
import random

class Layout:
    def draw_room_from_point (self, grid, x, y, size):
        len =  size
        for i in range(len):
            grid.place_agent(Wall(i, self), (x+i, y))
            grid.place_agent(Wall(i, self), (x+i, y-len))
            grid.place_agent(Wall(i, self), (x, y-i))
            grid.place_agent(Wall(i, self), (x+len, y-i))

    def draw_block_from_point (self, grid, x, y, width, height):
        for w in range(width):
            for h in range(height):
                grid.place_agent(Wall(w+h, self), (x+w, y+h))


    def draw(self, grid):

        self.draw_block_from_point(grid, 1, 4, 2, 10)
        self.draw_block_from_point(grid, 4, 4, 2, 10)
        self.draw_block_from_point(grid, 7, 4, 2, 10)

        self.draw_block_from_point(grid, 0, 0, 1, 18)
        self.draw_block_from_point(grid, 9, 0, 1, 18)
        self.draw_block_from_point(grid, 1, 0, 8, 1)
        self.draw_block_from_point(grid, 1, 17, 8, 1)


    def draw__(self, grid):
        self.draw_room_from_point(grid, 0,59, 20)
        self.draw_room_from_point(grid, 0,20, 20)

        self.draw_room_from_point(grid, 39,59, 20)
        self.draw_room_from_point(grid, 39,20, 20)

    def draw_(self, grid):
        # layout, walls
        for i in range(10):
            wall = Wall(i, self)

            #add to grid
            x = random.randrange(grid.width)
            y = random.randrange(grid.height)
            grid.place_agent(wall, (x,y)) # agent.pos has (x,y)
