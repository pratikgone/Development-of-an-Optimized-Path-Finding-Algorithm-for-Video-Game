# -*- coding: utf-8 -*-
"""
Development of  an Optimized path finding algorithm for video game

Description:
    This Development of  an Optimized path finding algorithm for video game allows users to explore 
    pathfinding algorithms on a grid. Users can set start and end points,
    add walls as obstacles, and watch as algorithms find paths around them.
    It also includes a random maze generator for diverse scenarios. 
    The real-time visualization helps users understand each algorithm's 
    approach to finding the shortest path. Perfect for learning and experimenting
    with pathfinding in a visually engaging way.
    
User interaction involve:
    1 - Right Click: To revert a start, end or wall to a normal cell
    2 - Left Click: To designate a normal cell as wall cell
    3 - Buttons: Choosing the pathfinding algorithm, generating a maze or clearing the grid
    
Note: After removing a start or end cell (by right click) user can reinstate
      them by left-clicking on any cell before starting an algorithm
    
Path Finding Algorithms used:
    1 - Dijkstra's Algorithm
    2 - A* Search Algorithm
    3 - Bidirectional Search
    4 - Breadth-First Search (BFS)
    5 - Depth-First Search (DFS)
"""
# Libraries ###################################################################
from os import startfile
import pygame
from heapq import heapify, heappush, heappop
import random
import time

# Variables ###################################################################
WIN_WIDTH = 1300
WIN_HEIGHT = 680

GRID_LEFT_BUFFER = 10
GRID_RIGHT_BUFFER = 10
GRID_TOP_BUFFER = 90
GRID_BOTTOM_BUFFER = 10
GRID_WIDTH = WIN_WIDTH - (GRID_LEFT_BUFFER + GRID_RIGHT_BUFFER)
GRID_HEIGHT = WIN_HEIGHT - (GRID_TOP_BUFFER + GRID_BOTTOM_BUFFER)

GRID_ROWS = 29 # Suggested Values - 29, 58, 116, 145, 290

BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255) # Background
GREEN = pygame.Color(34, 221, 34) # Start
RED = pygame.Color(255, 60, 26) # End
DARK_SLATE_GRAY = pygame.Color(38, 64, 64) # Wall and Grid Lines
GOLD = pygame.Color(255, 215, 0) # Path
LIGHT_GRAY = pygame.Color(179, 179, 179) # Visited
DODGER_BLUE = pygame.Color(30, 144, 255) # In Queue
DARK_ORANGE_RED = pygame.Color(179, 48, 0) # Path Not Found

LIGHT_RED = pygame.Color(255, 125, 102) # Clear Button
ORANGE = pygame.Color(255, 165, 0) # Generate Maze Button
LIGHT_ORANGE = pygame.Color(255, 193, 77) # Generate Maze Button
LAPIS_LAZULI = pygame.Color(34, 87, 122) # Dijkstra Button
LIGHT_LAPIS_LAZULI = pygame.Color(56, 142, 199) # Dijkstra Button
VERDIGRIS = pygame.Color(56, 163, 165) # A* Button
LIGHT_VERDIGRIS = pygame.Color(65, 188, 190) # A* Button
EMERALD = pygame.Color(87, 204, 153) # Bidirectional Button
LIGHT_EMERALD = pygame.Color(118, 213, 172) # Bidirectional Button
LIGHT_GREEN_1 = pygame.Color(128, 237, 153) # BFS button
LIGHT_GREEN_2 = pygame.Color(166, 242, 184) # BFS button
TEA_GREEN = pygame.Color(199, 249, 204) # DFS button
DARK__TEA_GREEN = pygame.Color(24, 231, 45) # DFS button

PAUSE_TIME = 0.01

total_time = 0.0
# Initial pygame Setup ########################################################
pygame.init()
pygame.display.set_caption("Path Finding Algorithms")
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
CLOCK = pygame.time.Clock()


# fro Box Class
class Box:
    def __init__(self, x, y, width, height, color="white", border_radius=0, text_surface=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.border_radius = border_radius
        self.text_surface = text_surface  # Surface for rendering text
        
        self.box_rect = pygame.Rect((self.x, self.y), (self.width, self.height))
        self.box_rect.topleft = (self.x, self.y)
    
    def set_color(self, color):
        """Set the primary color of the box."""
        self.color = color
    
    def set_border_radius(self, border_radius):
        """Set the border radius for rounded corners."""
        self.border_radius = border_radius
    
    def set_text(self, text_surface):
        """Set the text to be displayed in the box."""
        self.text_surface = text_surface
    
    def draw(self, surface):
        """Draw the box and its text on the given surface."""
        # Draw the box
        pygame.draw.rect(surface, self.color, self.box_rect, border_radius=self.border_radius)
        
        # Draw the text if provided
        if self.text_surface:
            text_rect = self.text_surface.get_rect(center=self.box_rect.center)
            surface.blit(self.text_surface, text_rect)

     

# Button Class ################################################################
class Button:
    def __init__(self, x, y, width, height, text_surface=None, border_radius=0, color="white"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text_surface = text_surface
        
        self.border_radius = border_radius
        self.primary_color = color
        self.dual_color = False
        
        self.button_rect = pygame.Rect((self.x, self.y), (self.width, self.height))
        self.button_rect.topleft = (self.x, self.y)
        self.clicked = False
    
    def set_primary_button_color(self, primary_color):
        self.primary_color = primary_color
    
    def set_secondary_button_color(self, secondary_color):
        self.dual_color = True
        self.secondary_color = secondary_color
    
    def add_text(self, text_surface):
        self.text_surface = text_surface
    
    def set_border_radius(self, border_radius):
        self.border_radius = border_radius
    
    def draw(self, surface):
        action = False
        
        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Check if mouse is over the button
        if self.button_rect.collidepoint(mouse_pos):
            if self.dual_color:
                pygame.draw.rect(surface, self.secondary_color, self.button_rect, border_radius=self.border_radius)
            else:
                pygame.draw.rect(surface, self.primary_color, self.button_rect, border_radius=self.border_radius)
            
            # Left Click
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                # To register the click only once
                self.clicked = True
                # Button is clicked
                action = True
            
            # To register the click only once
            if not pygame.mouse.get_pressed()[0]:
                self.clicked = False
        # If mouse is not over button
        else:
            pygame.draw.rect(surface, self.primary_color, self.button_rect, border_radius=self.border_radius)
        
        # Check if pygame surface for text is provided
        if self.text_surface:
            centered_text_rect = self.text_surface.get_rect(center=self.button_rect.center)
            surface.blit(self.text_surface, centered_text_rect)
        
        return action

# Cell Class ##################################################################
class Cell:
    def __init__(self, row, col, size, total_rows, total_cols, is_sizeXsize=True):
        self.row = row
        self.col = col
        self.size = size
        self.x = col * size + GRID_LEFT_BUFFER
        self.y = row * size + GRID_TOP_BUFFER
        self.color = WHITE
        self.neighbors = []
        self.total_rows = total_rows
        self.total_cols = total_cols
        self.is_sizeXsize = True
        self.cell_properties = {
                                "start": False,
                                "end": False,
                                "wall": False,
                                "visited": False,
                                "unvisited": True,
                                "in_queue": False,
                                "path": False,
                                "no_path": False
                                }
    
    # Only one property of cell can be True at a time
    def _manage_cell_property(current_cell_property, cell_properties):
        if current_cell_property not in cell_properties:
            print("Cell Property not found")
            return False
        
        for cell_property in cell_properties:
            cell_properties[cell_property] = False
        
        cell_properties[current_cell_property] = True
        return cell_properties
    
    def get_position(self):
        return self.row, self.col
    
    def is_start(self):
        return self.cell_properties["start"]
    
    def is_end(self):
        return self.cell_properties["end"]
    
    def is_wall(self):
        return self.cell_properties["wall"]
    
    def is_visited(self):
        return self.cell_properties["visited"]
    
    def is_unvisited(self):
        return self.cell_properties["unvisited"]
    
    def is_in_queue(self):
        return self.cell_properties["in_queue"]
    
    def is_path(self):
        return self.cell_properties["path"]
    
    def is_no_path(self):
        return self.cell_properties["no_path"]
    
    def set_start(self):
        if not self.is_end():
            self.cell_properties = Cell._manage_cell_property("start", self.cell_properties)
            self.color = GREEN
    
    def set_end(self):
        if not self.is_start():
            self.cell_properties = Cell._manage_cell_property("end", self.cell_properties)
            self.color = RED
    
    def set_wall(self):
        if not self.is_start() and not self.is_end():
            self.cell_properties = Cell._manage_cell_property("wall", self.cell_properties)
            self.color = DARK_SLATE_GRAY
    
    def set_visited(self):
        self.cell_properties = Cell._manage_cell_property("visited", self.cell_properties)
        self.color = LIGHT_GRAY
    
    def set_unvisited(self):
        self.cell_properties = Cell._manage_cell_property("unvisited", self.cell_properties)
        self.color = WHITE
    
    def set_in_queue(self):
        self.cell_properties = Cell._manage_cell_property("in_queue", self.cell_properties)
        self.color = DODGER_BLUE
    
    def set_path(self):
        self.cell_properties = Cell._manage_cell_property("path", self.cell_properties)
        self.color = GOLD
    
    def set_no_path(self):
        self.cell_properties = Cell._manage_cell_property("no_path", self.cell_properties)
        self.color = DARK_ORANGE_RED
    
    def reset(self):
        self.cell_properties = Cell._manage_cell_property("unvisited", self.cell_properties)
        self.color = WHITE
        
    def update_neighbors(self, grid):
        self.neighbors = []
        
        # Check Up
        if self.row > 0 and not grid[self.row - 1][self.col].is_wall():
            self.neighbors.append(grid[self.row - 1][self.col])
        
        # Check Down
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_wall():
            self.neighbors.append(grid[self.row + 1][self.col])
        
        # Check Left
        if self.col > 0 and not grid[self.row][self.col - 1].is_wall():
            self.neighbors.append(grid[self.row][self.col - 1])
        
        # Check Right
        if self.col < self.total_cols - 1 and not grid[self.row][self.col + 1].is_wall():
            self.neighbors.append(grid[self.row][self.col + 1])
    
    def draw(self, win):
        if self.is_sizeXsize:
            pygame.draw.rect(win, self.color, (self.x, self.y, self.size, self.size))
        else:
            pygame.draw.rect(win, self.color, (self.x, self.y, WIN_WIDTH - GRID_RIGHT_BUFFER, self.size))
    
    def __lt__(self, other):
        return False

# Dijkstra's Algorithm ########################################################
def  dijkstra_algorithm(draw, grid, start, end):
    global total_time
    node_data = {}
    
    for row in grid:
        for cell in row:
            node_data[cell] = {'cost': float("inf"), 'previous': []}
    
    node_data[start]['cost'] = 0
    visited_nodes = set()
    
    queue = []
    heappush(queue, (node_data[start]['cost'], start))
    
    # Start the timer
    start_time = time.time()
    
    while queue:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        # Display elapsed time per second
        current_time = time.time()
        elapsed_time = current_time - start_time
        print(f"Elapsed time: {elapsed_time:.2f} seconds", end="\r")
        
        heapify(queue)
        current = heappop(queue)[1]
        
        if current == end:
            path = node_data[end]['previous']
            path.append(end)
            draw_path(draw, start, end, path)
            
            # Stop the timer and calculate final elapsed time
            end_time = time.time()
            total_time = end_time - start_time
            print(f"\nTask completed in {total_time:.2f} seconds")

            

            return True
        
        if current not in visited_nodes:
            visited_nodes.add(current)
            if current != start:
                current.set_visited()
            
            for neighbor in current.neighbors:
                if neighbor not in visited_nodes:
                    # cost = cost till now + cost to reach that neighbor
                    cost = node_data[current]['cost'] + 1
                    if cost < node_data[neighbor]['cost']:
                        node_data[neighbor]['cost'] = cost
                        node_data[neighbor]['previous'] = node_data[current]['previous'].copy()
                        node_data[neighbor]['previous'].append(current)
                    heappush(queue, (node_data[neighbor]['cost'], neighbor))
                    neighbor.set_in_queue()
        
        draw()
        time.sleep(PAUSE_TIME)
    
    # Stop the timer if no path found
    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nTask completed in {total_time:.2f} seconds (no path found)")
    return False


# A* Search Algorithm #########################################################
def heuristic_function(p1, p2):
    # Using Manhattan Distance
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def construct_path(previous, current, start):
    # Constructing a list which shows path from Start to End
    path = [current]
    
    while current != start:
        current = previous[current]
        current.set_path()
        path.append(current)
    
    path.reverse()
    return path

def a_star_search_algorithm(draw, grid, start, end):
    global total_time
    g_score = {cell: float("inf") for row in grid for cell in row}
    g_score[start] = 0
    
    h_score = heuristic_function(start.get_position(), end.get_position())
    
    f_score = {cell: float("inf") for row in grid for cell in row}
    f_score[start] = g_score[start] + h_score
    
    queue = []
    heapify(queue)
    heappush(queue, (0, h_score, start))
    previous = {}
    
    # Start the timer
    start_time = time.time()
    
    while queue:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        # Display elapsed time per second
        current_time = time.time()
        elapsed_time = current_time - start_time
        print(f"Elapsed time: {elapsed_time:.2f} seconds", end="\r")
        
        current = heappop(queue)[2]
        
        if current != start:
            current.set_visited()
        
        if current == end:
            path = construct_path(previous, current, start)
            draw_path(draw, start, end, path)
            
            # Stop the timer and calculate final elapsed time
            end_time = time.time()

            total_time= end_time - start_time
            print(f"\nTask completed in {total_time:.2f} seconds")

            return True
        
        for neighbor in current.neighbors:
            # temp_g_score = current_g_score + score_to_reach_neighbor
            temp_g_score = g_score[current] + 1
            
            if temp_g_score < g_score[neighbor]:
                g_score[neighbor] = temp_g_score
                previous[neighbor] = current
                h_score = heuristic_function(neighbor.get_position(), end.get_position())
                f_score[neighbor] = g_score[neighbor] + h_score
                
                if neighbor not in queue:
                    heappush(queue, (f_score[neighbor], h_score, neighbor))
                    neighbor.set_in_queue()
        
        draw()
        time.sleep(PAUSE_TIME)
    
    # Stop the timer if no path found
    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nTask completed in {total_time:.2f} seconds (no path found)")
    return False


# # Bidirectional Search Algorithm ##############################################
def bidirectional_search_algorithm(draw, grid, start, end):
    global total_time
    start_queue = [start]
    end_queue = [end]
    
    start_visited = set()
    end_visited = set()
    
    start_prev_node = {cell: [] for row in grid for cell in row}
    end_prev_node = {cell: [] for row in grid for cell in row}
    
    intersection = None

    # Start the timer
    start_time = time.time()
    
    while start_queue and end_queue:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        # Display elapsed time per second
        current_time = time.time()
        elapsed_time = current_time - start_time
        total_time += elapsed_time  # Update total time
        print(f"Elapsed time: {elapsed_time:.2f} seconds", end="\r")
        
        # Expand from the start
        start_current = start_queue.pop(0)
        if start_current not in start_visited:
            start_visited.add(start_current)
            if start_current != start:
                start_current.set_visited()
            
            for neighbor in start_current.neighbors:
                if neighbor not in start_visited:
                    start_queue.append(neighbor)
                    if neighbor != start and neighbor != end:
                        neighbor.set_in_queue()
                    start_prev_node[neighbor] = start_prev_node[start_current].copy()
                    start_prev_node[neighbor].append(start_current)
                    if neighbor in end_visited:
                        intersection = neighbor
                        break
        
        if intersection:
            break
        
        # Expand from the end
        end_current = end_queue.pop(0)
        if end_current not in end_visited:
            end_visited.add(end_current)
            if end_current != end:
                end_current.set_visited()
            
            for neighbor in end_current.neighbors:
                if neighbor not in end_visited:
                    end_queue.append(neighbor)
                    if neighbor != start and neighbor != end:
                        neighbor.set_in_queue()
                    end_prev_node[neighbor] = end_prev_node[end_current].copy()
                    end_prev_node[neighbor].append(end_current)
                    if neighbor in start_visited:
                        intersection = neighbor
                        break
        
        if intersection:
            break
        
        draw()
        time.sleep(PAUSE_TIME)
    
    if intersection:
        # Combine paths from start to the intersection and end to the intersection
        path = start_prev_node[intersection].copy()
        path.append(intersection)
        path.extend(reversed(end_prev_node[intersection]))
        draw_path(draw, start, end, path)

        # Stop the timer and display the final time
        end_time = time.time()
        total_time = end_time - start_time
        print(f"\nTask completed in {total_time:.2f} seconds")
        return True
    
    # Stop the timer if no path is found
    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nTask completed in {total_time:.2f} seconds (no path found)")
    return False


# Random Maze Generator #######################################################
def recursive_division(x, y, width, height, grid, draw, horizontal):
    # Generate Random Maze using recursive division
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
           pygame.quit()
    
    if width < 3 or height < 3:
        return

    if horizontal:
        wall_y = random.randint(y + 1, y + height - 2)
        for col in range(x, x + width):
            grid[wall_y][col-1].set_wall()
        gap_x = random.randint(x, x + width - 3)
        grid[wall_y][gap_x].set_unvisited()
        draw()
        time.sleep(PAUSE_TIME)
        
        recursive_division(x, y, width, wall_y - y, grid, draw, not horizontal)
        recursive_division(x, wall_y + 1, width, y + height - wall_y - 1, grid, draw, not horizontal)
    else:
        wall_x = random.randint(x + 1, x + width - 2)
        for row in range(y, y + height):
            grid[row-1][wall_x].set_wall()
        gap_y = random.randint(y, y + height - 3)
        grid[gap_y][wall_x].set_unvisited()
        draw()
        time.sleep(PAUSE_TIME)

        recursive_division(x, y, wall_x - x, height, grid, draw, not horizontal)
        recursive_division(wall_x + 1, y, x + width - wall_x - 1, height, grid, draw, not horizontal)
    return

def generate_random_maze(x, y, width, height, grid, draw):
    horizontal = random.choice([True, False])
    for cell in grid[0]:
        cell.set_wall()
        draw()
    for row in range(height):
        grid[row][0].set_wall()
        draw()
    for cell in grid[height - 1]:
        cell.set_wall()
        draw()
    for row in range(height):
        grid[row][width - 1].set_wall()
        draw()
    recursive_division(1, 1, width-1, height-1, grid, draw, horizontal)
    return

# Grid Functions ##############################################################
def generate_grid(rows, grid_width, grid_height):
    grid = []
    cell_size = grid_height // rows
    cols = grid_width // cell_size
    
    for i in range(rows):
        grid.append([])
        for j in range(cols):
            cell = Cell(i, j, cell_size, rows, cols)
            grid[i].append(cell)
    
    if grid_width % cell_size != 0:
        for i in range(rows):
            cell = Cell(i, cols, cell_size, rows, cols, is_sizeXsize=False)
            grid[i].append(cell)
    
    return grid

def draw_grid_lines(win, rows, grid_width, grid_height):
    cell_size = grid_height // rows
    
    for i in range(rows):
        pygame.draw.line(win, DARK_SLATE_GRAY, (GRID_LEFT_BUFFER, (i*cell_size) + GRID_TOP_BUFFER), (WIN_WIDTH - GRID_RIGHT_BUFFER, (i*cell_size) + GRID_TOP_BUFFER))
    
    pygame.draw.line(win, DARK_SLATE_GRAY, (GRID_LEFT_BUFFER, WIN_HEIGHT - GRID_BOTTOM_BUFFER), (WIN_WIDTH - GRID_RIGHT_BUFFER, WIN_HEIGHT - GRID_BOTTOM_BUFFER))
    
    cols = grid_width // cell_size
    
    for i in range(cols):
        pygame.draw.line(win, DARK_SLATE_GRAY, ((i*cell_size) + GRID_LEFT_BUFFER, GRID_TOP_BUFFER), ((i*cell_size) + GRID_LEFT_BUFFER, WIN_HEIGHT - GRID_BOTTOM_BUFFER))
        
    pygame.draw.line(win, DARK_SLATE_GRAY, (WIN_WIDTH - GRID_RIGHT_BUFFER, GRID_TOP_BUFFER), (WIN_WIDTH - GRID_RIGHT_BUFFER, WIN_HEIGHT - GRID_BOTTOM_BUFFER))
    
def draw_grid(win, grid, rows, grid_width, grid_height):
    # win.fill(WHITE)
    for row in grid:
        for cell in row:
            cell.draw(win)
    
    draw_grid_lines(win, rows, grid_width, grid_height)
    pygame.display.update()

def reset_grid(grid):
    for row in grid:
        for cell in row:
            cell.set_unvisited()
    
    pygame.display.update()

def click_in_grid(click_pos):
    x, y = click_pos
    if x >= GRID_LEFT_BUFFER and x < (WIN_WIDTH - GRID_RIGHT_BUFFER) and y >= GRID_TOP_BUFFER and y < (WIN_HEIGHT - GRID_BOTTOM_BUFFER):
        # Mouse clicked inside the grid
        return True
    return False
    
def get_clicked_cell(click_pos, rows, grid_width, grid_height):
    cell_size = grid_height // rows
    x, y = click_pos
    
    row = (y - GRID_TOP_BUFFER) // cell_size
    col = (x - GRID_LEFT_BUFFER) // cell_size
    return row, col

def draw_path(draw, start, end, path):
    for cell in path:
        if cell == start:
            cell.set_start()
        elif cell == end:
            cell.set_end()
        else:
            cell.set_path()
        draw()

def draw_path_not_found(win, draw, grid, rows, grid_width, grid_height):
    # win.fill(WHITE)
    
    for row in grid:
        for cell in row:
            if cell.is_visited() or cell.is_in_queue():
                cell.set_no_path()
    
    draw()
    time.sleep(0.6)
    
    for i in range(6):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
               pygame.quit()
        
        for row in grid:
            for cell in row:
                if cell.is_no_path():
                    cell.set_unvisited()
                elif cell.is_unvisited():
                    cell.set_no_path()
        draw()
        time.sleep(0.6)
    
    draw_grid_lines(win, rows, grid_width, grid_height)
    pygame.display.update()


 # Timer Display...
spacing = 5
time_box_width = 180
time_box_height = 45
time_box_radius = 30
time_box_font = pygame.font.SysFont("Georgia", 15, bold=False, italic=False)

# Buttons #####################################################################
# Values for Window Size = 1300X680 and Grid Size = 1280X580
spacing = 5
button_width = 180
button_height = 45
button_radius = 30
button_font = pygame.font.SysFont("Georgia", 15, bold=False, italic=False)

# Algorithm Buttons
dijkstra_surf = button_font.render("Dijkstra's Algorithm", True, BLACK)
dijkstra_button = Button(spacing, 5, button_width, button_height, text_surface=dijkstra_surf, border_radius=button_radius, color=LAPIS_LAZULI)
dijkstra_button.set_secondary_button_color(LIGHT_LAPIS_LAZULI)

a_star_surf = button_font.render("A* Search", True, BLACK)
a_star_button = Button((2*spacing) + button_width, 5, button_width, button_height, text_surface=a_star_surf, border_radius=button_radius, color=VERDIGRIS)
a_star_button.set_secondary_button_color(LIGHT_VERDIGRIS)

bidirectional_surf = button_font.render("Bidirectional Search", True, BLACK)
bidirectional_button = Button((3*spacing) + (2*button_width), 5, button_width, button_height, text_surface=bidirectional_surf, border_radius=button_radius, color=EMERALD)
bidirectional_button.set_secondary_button_color(LIGHT_EMERALD)





# Clear Button
clear_surf = button_font.render("CLEAR", True, BLACK)
clear_button = Button((6*spacing) + (5*button_width), 5, button_width, button_height, text_surface=clear_surf, border_radius=button_radius, color=RED)
clear_button.set_secondary_button_color(LIGHT_RED)

# Random Maze Button
maze_surf = button_font.render("Generate Random Maze", True, BLACK)
maze_button = Button((7*spacing) + (6*button_width), 5, button_width, button_height, text_surface=maze_surf, border_radius=button_radius, color=ORANGE)
maze_button.set_secondary_button_color(LIGHT_ORANGE)

# Helper Functions ############################################################
def update_cell_neighbors(grid):
    for row in grid:
        for cell in row:
            cell.update_neighbors(grid)
    return

def draw_stationary_objects(win):
    pygame.draw.rect(win, DARK_SLATE_GRAY, (0, 0, WIN_WIDTH, 55))
    
    # Algorithm buttons
    dijkstra_button.draw(win)
    a_star_button.draw(win)
    bidirectional_button.draw(win)

    global spacing
    # box for timer
    box_time_draw_surf = time_box_font.render(f"Task Time: {total_time.__round__(2)}", True, BLACK)
    box_time = Box((4 * spacing) + (3 * time_box_width), 5, time_box_width, time_box_height,
                   text_surface=box_time_draw_surf, border_radius=time_box_radius, color=EMERALD)
   
   
    # print(f"In draw function : {total_time}")
    box_time.draw(win)

    
    # Clear button
    clear_button.draw(win)
    
    # Generate Random Maze button
    maze_button.draw(win)
    
    # Legend
    # Values for Window Size = 1300X680 and Grid Size = 1280X580
    cube_size = 25
    spacing = 5
    legend_font = pygame.font.SysFont("Georgia", 20, bold=False, italic=False)
    
    # Legend - Start
    pygame.draw.rect(win, GREEN, (GRID_LEFT_BUFFER + 20, GRID_TOP_BUFFER - (cube_size + 5), cube_size, cube_size))
    text_visited_surf = legend_font.render("Start Cell", True, DARK_SLATE_GRAY)
    win.blit(text_visited_surf, (GRID_LEFT_BUFFER + cube_size + spacing + 20, GRID_TOP_BUFFER - (cube_size + 5)))
    
    # Legend - End
    pygame.draw.rect(win, RED, (GRID_LEFT_BUFFER + 216, GRID_TOP_BUFFER - (cube_size + 5), cube_size, cube_size))
    text_visited_surf = legend_font.render("End Cell", True, DARK_SLATE_GRAY)
    win.blit(text_visited_surf, (GRID_LEFT_BUFFER + cube_size + spacing + 216, GRID_TOP_BUFFER - (cube_size + 5)))
    
    # Legend - Wall
    pygame.draw.rect(win, DARK_SLATE_GRAY, (GRID_LEFT_BUFFER + 416, GRID_TOP_BUFFER - (cube_size + 5), cube_size, cube_size))
    text_visited_surf = legend_font.render("Wall/Obstacle Cell", True, DARK_SLATE_GRAY)
    win.blit(text_visited_surf, (GRID_LEFT_BUFFER + cube_size + spacing + 416, GRID_TOP_BUFFER - (cube_size + 5)))
    
    # Legend - Unvisited
    pygame.draw.rect(win, DARK_SLATE_GRAY, (GRID_LEFT_BUFFER + 696, GRID_TOP_BUFFER - (cube_size + 5), cube_size, cube_size), width=1)
    text_visited_surf = legend_font.render("Unvisited Cells", True, DARK_SLATE_GRAY)
    win.blit(text_visited_surf, (GRID_LEFT_BUFFER + cube_size + spacing + 696, GRID_TOP_BUFFER - (cube_size + 5)))
    
    # Legend - Visited Cells
    pygame.draw.rect(win, DODGER_BLUE, (GRID_LEFT_BUFFER + 956, GRID_TOP_BUFFER - (cube_size + 5), cube_size, cube_size))
    pygame.draw.rect(win, LIGHT_GRAY, (GRID_LEFT_BUFFER + 986, GRID_TOP_BUFFER - (cube_size + 5), cube_size, cube_size))
    text_visited_surf = legend_font.render("Visited Cells", True, DARK_SLATE_GRAY)
    win.blit(text_visited_surf, (GRID_LEFT_BUFFER + cube_size + spacing + 986, GRID_TOP_BUFFER - (cube_size + 5)))
    
    # Legend - Path
    pygame.draw.rect(win, GOLD, (GRID_LEFT_BUFFER + 1190, GRID_TOP_BUFFER - (cube_size + 5), cube_size, cube_size))
    text_visited_surf = legend_font.render("Path", True, DARK_SLATE_GRAY)
    win.blit(text_visited_surf, (GRID_LEFT_BUFFER + cube_size + spacing + 1190, GRID_TOP_BUFFER - (cube_size + 5)))
    return

# Main Function ###############################################################
def main(win, rows, grid_width, grid_height):
    grid = generate_grid(rows, grid_width, grid_height)
    cols = len(grid[0])
    
    START = grid[random.randrange(0, rows, 2)][random.randrange(0, cols, 2)]
    START.set_start()
    END = grid[random.randrange(0, rows, 3)][random.randrange(0, cols, 3)]
    END.set_end()
    
    running = True
    algorithm_started = False
    algorithm_completed = False
    path_found = False
    
    while running:
        WIN.fill(WHITE) # Refresh the screen to clear the previous content
        
        draw_stationary_objects(win)
        draw_grid(win, grid, rows, grid_width, grid_height)
        
        for event in pygame.event.get():
            # User can press X (close button) to quit anytime
            if event.type == pygame.QUIT:
               running = False
               break
            
            # User should not be able to change anything while an algorithm is running
            # User can still quit anytime
            if algorithm_started:
                continue
            
            # User can click CLEAR button to clear the grid
            if clear_button.draw(win):
                algorithm_completed = False
                path_found = False
                reset_grid(grid)
                global total_time
                total_time = 0.0
                if START:
                    START.set_start()
                if END:
                    END.set_end()
            
            # User should not be able to change grid after an algorithm is completed
            # User can still clear the grid
            if algorithm_completed:
                continue
            
            # Left click
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                if click_in_grid(pos):
                    row, col = get_clicked_cell(pos, rows, grid_width, grid_height)
                    cell = grid[row][col]
                    if not START and cell != END:
                        START = cell
                        START.set_start()
                    elif not END and cell != START:
                        END = cell
                        END.set_end()
                    elif cell != START and cell != END:
                        cell.set_wall()
            
            # Right click
            if pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()    
                if click_in_grid(pos):
                    row, col = get_clicked_cell(pos, rows, grid_width, grid_height)
                    cell = grid[row][col]
                    cell.reset()
                    if cell == START:
                        START = None
                    elif cell == END:
                        END = None
            
            # Generate Random Maze
            if maze_button.draw(win) and not algorithm_started:
                algorithm_started = True
                reset_grid(grid)
                if START:
                    START.set_start()
                if END:
                    END.set_end()
                generate_random_maze(0, 0, cols, rows, grid, lambda: draw_grid(win, grid, rows, grid_width, grid_height))
                algorithm_started = False
            
            if not algorithm_started and START and END:
                # Start Dijkstra's algorithm
                if dijkstra_button.draw(win):
                    algorithm_started = True
                    update_cell_neighbors(grid)
                    path_found = dijkstra_algorithm(lambda: draw_grid(win, grid, rows, grid_width, grid_height), grid, START, END)
                    if not path_found:
                        draw_path_not_found(win, lambda: draw_grid(win, grid, rows, grid_width, grid_height), grid, rows, grid_width, grid_height)
                    algorithm_started = False
                    algorithm_completed = True
                # Start A* Search algorithm
                elif a_star_button.draw(win):
                    algorithm_started = True
                    update_cell_neighbors(grid)
                    path_found= a_star_search_algorithm(lambda: draw_grid(win, grid, rows, grid_width, grid_height), grid, START, END)


                    if not path_found:
                        draw_path_not_found(win, lambda: draw_grid(win, grid, rows, grid_width, grid_height), grid, rows, grid_width, grid_height)
                    algorithm_started = False
                    algorithm_completed = True
                # Start Bidirectional Search algorithm
                elif bidirectional_button.draw(win):
                    algorithm_started = True
                    update_cell_neighbors(grid)
                    path_found = bidirectional_search_algorithm(lambda: draw_grid(win, grid, rows, grid_width, grid_height), grid, START, END)
                    if not path_found:
                        draw_path_not_found(win, lambda: draw_grid(win, grid, rows, grid_width, grid_height), grid, rows, grid_width, grid_height)
                    algorithm_started = False
                    algorithm_completed = True

                    
             
        
        # Update the screen to show the content
        pygame.display.update()
        # Limit FPS to 60
        CLOCK.tick(60)
        
    pygame.quit()
    return
main(WIN, GRID_ROWS, GRID_WIDTH, GRID_HEIGHT)