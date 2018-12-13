from objects import Wall, Shelf, ActionCenter
from agent import AgentBasic

# ALL THE SHELVES
class Layout:
    width = 20
    height = 16

    def draw_block_from_point (self, grid, x, y, width, height, cls):
        cells = []
        for w in range(width):
            for h in range(height):
                cell = (x+w, y+h)
                cells.append(cell)
                grid.place_agent(cls(w+h, self), cell)
        return cells

    def draw_room_from_point (self, grid, x, y, width, height):
        for i in range(width):
            self.draw_block_from_point(grid, x+i, y, 1, height, Wall)

    def create_world(self, model, play_guessing):
        # Side walls
        self.draw_block_from_point(model.grid, 0, 1, 1, 14, Wall)
        self.draw_block_from_point(model.grid, 10, 1, 1, 9, Wall)

        # Top and bottom
        self.draw_block_from_point(model.grid, 0, 0, 11, 1, Wall)
        self.draw_block_from_point(model.grid, 0, 15, 20, 1, Wall)

        #Corner
        self.draw_room_from_point(model.grid, 11, 0, 9, 9)

        # Horizontal shelf area walls
        self.draw_block_from_point(model.grid, 11, 9, 9, 1, Wall)
        self.draw_block_from_point(model.grid, 19, 10, 1, 5, Wall)


        shelf_cells = []

        # Vertical shelves
        shelf_cells += self.draw_block_from_point(model.grid, 1, 1, 1, 8, Shelf)
        # self.draw_block_from_point(model.grid, 1, 1, 1, 8, Shelf)
        shelf_cells += self.draw_block_from_point(model.grid, 3, 1, 1, 8, Shelf)
        shelf_cells += self.draw_block_from_point(model.grid, 5, 1, 1, 8, Shelf)
        shelf_cells += self.draw_block_from_point(model.grid, 7, 1, 1, 8, Shelf)
        # self.draw_block_from_point(model.grid, 7, 1, 1, 8, Shelf)
        shelf_cells += self.draw_block_from_point(model.grid, 9, 1, 1, 8, Shelf)
        # self.draw_block_from_point(model.grid, 9, 1, 1, 8, Shelf)

        # Horizontal shelves
        shelf_cells += self.draw_block_from_point(model.grid, 11, 10, 8, 1, Shelf)
        shelf_cells += self.draw_block_from_point(model.grid, 11, 12, 8, 1, Shelf)
        shelf_cells += self.draw_block_from_point(model.grid, 11, 14, 8, 1, Shelf)

        # Action center
        action_center = ActionCenter(0, model, shelf_cells)
        model.grid.place_agent(action_center, (5, 12))

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
