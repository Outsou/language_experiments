from objects import Wall, Shelf, ActionCenter, Beer
from mesa.space import SingleGrid


def draw_block_from_point(model, x, y, width, height, cls):
    cells = []
    for w in range(width):
        for h in range(height):
            cell = (x + w, y + h)
            cells.append(cell)
            model.grid.place_agent(cls(w + h, model), cell)
    return cells

class BeerOnlyEnvironment:
    width = 17
    height = 20
    name = 'beer_only'

    @staticmethod
    def create_env(model):
        model.grid = SingleGrid(BeerOnlyEnvironment.width, BeerOnlyEnvironment.height, False)  # True=toroidal

        # Side walls
        draw_block_from_point(model, 0, 1, 1, 18, Wall)
        draw_block_from_point(model, 16, 1, 1, 18, Wall)

        # Bottom and top
        draw_block_from_point(model, 0, 0, 17, 1, Wall)
        draw_block_from_point(model, 0, 19, 17, 1, Wall)

        shelf_cells = []

        # Shelves
        shelf_cells += draw_block_from_point(model, 1, 15, 1, 4, Shelf)
        shelf_cells += draw_block_from_point(model, 15, 15, 1, 4, Shelf)

        # Action center
        action_center = ActionCenter(0, model, shelf_cells)
        model.grid.place_agent(action_center, (8, 3))

        # Beer
        draw_block_from_point(model, 1, 7, 2, 8, Beer)
        draw_block_from_point(model, 4, 7, 2, 8, Beer)
        draw_block_from_point(model, 7, 7, 3, 8, Beer)
        draw_block_from_point(model, 8, 15, 1, 4, Beer)
        draw_block_from_point(model, 11, 7, 2, 8, Beer)
        draw_block_from_point(model, 14, 7, 2, 8, Beer)

        return {'action_center': action_center}

class BeerEnvironment:
    width = 25
    height = 29
    name = 'beer'

    @staticmethod
    def create_env(model):
        model.grid = SingleGrid(BeerEnvironment.width, BeerEnvironment.height, False)  # True=toroidal

        # Side walls
        draw_block_from_point(model, 0, 13, 1, 15, Wall)
        draw_block_from_point(model, 15, 1, 1, 9, Wall)

        # Bottom left corner
        draw_block_from_point(model, 0, 0, 6, 13, Wall)

        # Top right corner
        draw_block_from_point(model, 15, 15, 10, 14, Wall)

        # Bottom right corner
        draw_block_from_point(model, 16, 0, 9, 9, Wall)

        # Horizontal shelf area walls
        draw_block_from_point(model, 16, 9, 9, 1, Wall)
        draw_block_from_point(model, 24, 10, 1, 5, Wall)

        # Bottom and top
        draw_block_from_point(model, 6, 0, 10, 1, Wall)
        draw_block_from_point(model, 0, 28, 15, 1, Wall)

        shelf_cells = []

        # Vertical shelves
        draw_block_from_point(model, 6, 1, 1, 8, Shelf)
        shelf_cells += draw_block_from_point(model, 8, 1, 1, 8, Shelf)
        shelf_cells += draw_block_from_point(model, 10, 1, 1, 8, Shelf)
        shelf_cells += draw_block_from_point(model, 12, 1, 1, 8, Shelf)
        draw_block_from_point(model, 14, 1, 1, 8, Shelf)

        # Horizontal shelves
        draw_block_from_point(model, 16, 10, 8, 1, Shelf)
        shelf_cells += draw_block_from_point(model, 16, 12, 8, 1, Shelf)
        draw_block_from_point(model, 16, 14, 8, 1, Shelf)

        # Action center
        action_center = ActionCenter(0, model, shelf_cells)
        model.grid.place_agent(action_center, (10, 12))

        # Beer
        draw_block_from_point(model, 1, 16, 2, 8, Beer)
        draw_block_from_point(model, 4, 16, 2, 8, Beer)
        draw_block_from_point(model, 7, 16, 2, 12, Beer)
        draw_block_from_point(model, 10, 16, 2, 8, Beer)
        draw_block_from_point(model, 13, 16, 2, 8, Beer)

        return {'action_center': action_center}

class DefaultEnvironment:
    width = 20
    height = 16
    name = 'default'

    @staticmethod
    def create_env(model):
        model.grid = SingleGrid(DefaultEnvironment.width, DefaultEnvironment.height, False)

        # Side walls
        draw_block_from_point(model, 0, 1, 1, 14, Wall)
        draw_block_from_point(model, 10, 1, 1, 9, Wall)

        # Top and bottom
        draw_block_from_point(model, 0, 0, 11, 1, Wall)
        draw_block_from_point(model, 0, 15, 20, 1, Wall)

        #Corner
        draw_block_from_point(model, 11, 0, 9, 9, Wall)

        # Horizontal shelf area walls
        draw_block_from_point(model, 11, 9, 9, 1, Wall)
        draw_block_from_point(model, 19, 10, 1, 5, Wall)

        shelf_cells = []

        # Vertical shelves
        # shelf_cells += self.draw_block_from_point(model.grid, 1, 1, 1, 8, Shelf)
        draw_block_from_point(model, 1, 1, 1, 8, Shelf)
        shelf_cells += draw_block_from_point(model, 3, 1, 1, 8, Shelf)
        shelf_cells += draw_block_from_point(model, 5, 1, 1, 8, Shelf)
        shelf_cells += draw_block_from_point(model, 7, 1, 1, 8, Shelf)
        # self.draw_block_from_point(model.grid, 7, 1, 1, 8, Shelf)
        # shelf_cells += self.draw_block_from_point(model.grid, 9, 1, 1, 8, Shelf)
        draw_block_from_point(model, 9, 1, 1, 8, Shelf)

        # Horizontal shelves
        # shelf_cells += self.draw_block_from_point(model.grid, 11, 10, 8, 1, Shelf)
        draw_block_from_point(model, 11, 10, 8, 1, Shelf)
        shelf_cells += draw_block_from_point(model, 11, 12, 8, 1, Shelf)
        # shelf_cells += self.draw_block_from_point(model.grid, 11, 14, 8, 1, Shelf)
        draw_block_from_point(model, 11, 14, 8, 1, Shelf)

        # Action center
        action_center = ActionCenter(0, model, shelf_cells)
        model.grid.place_agent(action_center, (5, 12))

        return {'action_center': action_center}

class DoubleEnvironment:
    width = 28
    height = 24
    name = 'double'

    @staticmethod
    def create_env(model):
        model.grid = SingleGrid(DoubleEnvironment.width, DoubleEnvironment.height, False)

        # Side walls
        draw_block_from_point(model, 0, 1, 1, 22, Wall)
        draw_block_from_point(model, 10, 1, 1, 17, Wall)

        # Top and bottom
        draw_block_from_point(model, 0, 0, 11, 1, Wall)
        draw_block_from_point(model, 0, 23, 28, 1, Wall)

        #Corner
        draw_block_from_point(model, 11, 0, 17, 17, Wall)

        # Horizontal shelf area walls
        draw_block_from_point(model, 11, 17, 17, 1, Wall)
        draw_block_from_point(model, 27, 18, 1, 5, Wall)

        shelf_cells = []

        # Vertical shelves
        # shelf_cells += self.draw_block_from_point(model.grid, 1, 1, 1, 16, Shelf)
        draw_block_from_point(model, 1, 1, 1, 16, Shelf)
        shelf_cells += draw_block_from_point(model, 3, 1, 1, 16, Shelf)
        shelf_cells += draw_block_from_point(model, 5, 1, 1, 16, Shelf)
        shelf_cells += draw_block_from_point(model, 7, 1, 1, 16, Shelf)
        # self.draw_block_from_point(model.grid, 7, 1, 1, 8, Shelf)
        # shelf_cells += self.draw_block_from_point(model.grid, 9, 1, 1, 16, Shelf)
        draw_block_from_point(model, 9, 1, 1, 16, Shelf)

        # Horizontal shelves
        # shelf_cells += self.draw_block_from_point(model.grid, 11, 18, 16, 1, Shelf)
        draw_block_from_point(model, 11, 18, 16, 1, Shelf)
        shelf_cells += draw_block_from_point(model, 11, 20, 16, 1, Shelf)
        # shelf_cells += self.draw_block_from_point(model.grid, 11, 22, 16, 1, Shelf)
        draw_block_from_point(model, 11, 22, 16, 1, Shelf)

        # Action center
        action_center = ActionCenter(0, model, shelf_cells)
        model.grid.place_agent(action_center, (5, 20))

        return {'action_center': action_center}

    # 5 SHELVES
    # class Layout:
    #     width = 11
    #     height = 13
    #
    #     def draw_block_from_point (self, grid, x, y, width, height, cls):
    #         cells = []
    #         for w in range(width):
    #             for h in range(height):
    #                 cell = (x+w, y+h)
    #                 cells.append(cell)
    #                 grid.place_agent(cls(w+h, self), cell)
    #         return cells
    #
    #     def create_world(self, model, play_guessing):
    #         # Side walls
    #         self.draw_block_from_point(model.grid, 0, 1, 1, 11, Wall)
    #         self.draw_block_from_point(model.grid, 10, 1, 1, 11, Wall)
    #
    #         # Top and bottom
    #         self.draw_block_from_point(model.grid, 0, 0, 11, 1, Wall)
    #         self.draw_block_from_point(model.grid, 0, 12, 11, 1, Wall)
    #
    #         shelf_cells = []
    #
    #         # Shelves
    #         shelf_cells += self.draw_block_from_point(model.grid, 1, 1, 1, 8, Shelf)
    #         # self.draw_block_from_point(model.grid, 1, 1, 1, 8, Shelf)
    #         shelf_cells += self.draw_block_from_point(model.grid, 3, 1, 1, 8, Shelf)
    #         shelf_cells += self.draw_block_from_point(model.grid, 5, 1, 1, 8, Shelf)
    #         shelf_cells += self.draw_block_from_point(model.grid, 7, 1, 1, 8, Shelf)
    #         # self.draw_block_from_point(model.grid, 7, 1, 1, 8, Shelf)
    #         shelf_cells += self.draw_block_from_point(model.grid, 9, 1, 1, 8, Shelf)
    #         # self.draw_block_from_point(model.grid, 9, 1, 1, 8, Shelf)
    #
    #         # Action center
    #         action_center = ActionCenter(0, model, shelf_cells)
    #         model.grid.place_agent(action_center, (5, 11))
    #
    #         return {'action_center': action_center}

    # 3 SHELVES
    # class Layout:
    #     width = 7
    #     height = 13
    #
    #     def draw_block_from_point (self, grid, x, y, width, height, cls):
    #         cells = []
    #         for w in range(width):
    #             for h in range(height):
    #                 cell = (x+w, y+h)
    #                 cells.append(cell)
    #                 grid.place_agent(cls(w+h, self), cell)
    #         return cells
    #
    #     def create_world(self, model, play_guessing):
    #         # Side walls
    #         self.draw_block_from_point(model.grid, 0, 1, 1, 11, Wall)
    #         self.draw_block_from_point(model.grid, 6, 1, 1, 11, Wall)
    #
    #         # Top and bottom
    #         self.draw_block_from_point(model.grid, 0, 0, 7, 1, Wall)
    #         self.draw_block_from_point(model.grid, 0, 12, 7, 1, Wall)
    #
    #         shelf_cells = []
    #
    #         # Shelves
    #         # shelf_cells += self.draw_block_from_point(model.grid, 1, 1, 1, 8, Shelf)
    #         self.draw_block_from_point(model.grid, 1, 1, 1, 8, Shelf)
    #         shelf_cells += self.draw_block_from_point(model.grid, 3, 1, 1, 8, Shelf)
    #         # shelf_cells += self.draw_block_from_point(model.grid, 5, 1, 1, 8, Shelf)
    #         self.draw_block_from_point(model.grid, 5, 1, 1, 8, Shelf)
    #
    #         # Action center
    #         action_center = ActionCenter(0, model, shelf_cells)
    #         model.grid.place_agent(action_center, (1, 11))
    #
    #         return {'action_center': action_center}

    # Horizontal only
    # class Layout:
    #     width = 16
    #     height = 7
    #
    #     def draw_block_from_point (self, grid, x, y, width, height, cls):
    #         cells = []
    #         for w in range(width):
    #             for h in range(height):
    #                 cell = (x+w, y+h)
    #                 cells.append(cell)
    #                 grid.place_agent(cls(w+h, self), cell)
    #         return cells
    #
    #     def draw_room_from_point (self, grid, x, y, width, height):
    #         for i in range(width):
    #             self.draw_block_from_point(grid, x+i, y, 1, height, Wall)
    #
    #     def create_world(self, model, play_guessing):
    #         # Side walls
    #         self.draw_block_from_point(model.grid, 0, 1, 1, 5, Wall)
    #         self.draw_block_from_point(model.grid, 15, 1, 1, 5, Wall)
    #
    #         # Top and bottom
    #         self.draw_block_from_point(model.grid, 0, 6, 16, 1, Wall)
    #         self.draw_block_from_point(model.grid, 0, 0, 16, 1, Wall)
    #
    #
    #         shelf_cells = []
    #
    #         # Horizontal shelves
    #         shelf_cells += self.draw_block_from_point(model.grid, 7, 1, 8, 1, Shelf)
    #         # self.draw_block_from_point(model.grid, 11, 10, 8, 1, Shelf)
    #         shelf_cells += self.draw_block_from_point(model.grid, 7, 3, 8, 1, Shelf)
    #         shelf_cells += self.draw_block_from_point(model.grid, 7, 5, 8, 1, Shelf)
    #         # self.draw_block_from_point(model.grid, 11, 14, 8, 1, Shelf)
    #
    #         # Action center
    #         action_center = ActionCenter(0, model, shelf_cells)
    #         model.grid.place_agent(action_center, (1, 3))
    #
    #         return {'action_center': action_center}