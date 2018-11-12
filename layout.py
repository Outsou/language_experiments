from objects import Wall, Shelf, ActionCenter
from agent import AgentBasic


class Layout:
    width = 7
    height = 13

    def draw_block_from_point (self, grid, x, y, width, height, cls):
        cells = []
        for w in range(width):
            for h in range(height):
                cell = (x+w, y+h)
                cells.append(cell)
                grid.place_agent(cls(w+h, self), cell)
        return cells

    def create_world(self, model, play_guessing):
        # Side walls
        self.draw_block_from_point(model.grid, 0, 1, 1, 11, Wall)
        self.draw_block_from_point(model.grid, 6, 1, 1, 11, Wall)

        # Top and bottom
        self.draw_block_from_point(model.grid, 0, 0, 7, 1, Wall)
        self.draw_block_from_point(model.grid, 0, 12, 7, 1, Wall)

        shelf_cells = []

        # Shelves
        shelf_cells += self.draw_block_from_point(model.grid, 1, 1, 1, 8, Shelf)
        shelf_cells += self.draw_block_from_point(model.grid, 3, 1, 1, 8, Shelf)
        shelf_cells += self.draw_block_from_point(model.grid, 5, 1, 1, 8, Shelf)

        # Action center
        action_center = ActionCenter(0, model, shelf_cells)
        model.grid.place_agent(action_center, (3, 11))

        return {'action_center': action_center}

