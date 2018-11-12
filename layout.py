from objects import Wall
import random

class Layout:
    width = 10
    height = 20

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
        # Middle left walls
        self.draw_block_from_point(grid, 1, 5, 2, 10)
        # self.draw_block_from_point(grid, 1, 6, 1, 8)

        # Middle middle wall
        self.draw_block_from_point(grid, 4, 5, 2, 10)

        # Middle right walls
        self.draw_block_from_point(grid, 7, 5, 2, 10)
        # self.draw_block_from_point(grid, 8, 6, 1, 8)

        # Surrounding walls
        self.draw_block_from_point(grid, 0, 1, 1, 18)
        self.draw_block_from_point(grid, 9, 1, 1, 18)
        self.draw_block_from_point(grid, 0, 0, 10, 1)
        self.draw_block_from_point(grid, 0, 19, 10, 1)
        # self.draw_block_from_point(grid, 2, 1, 6, 1)
        # self.draw_block_from_point(grid, 2, 18, 6, 1)
