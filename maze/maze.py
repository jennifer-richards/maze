import random

class DeadEnd(Exception):
    pass

class Maze:
    door = dict(N=1, E=2, S=4, W=8) # values in the grid represent openings
    door_name = {1:"N", 2:"E", 4:"S", 8:"W"}

    dx = {"E":1, door["E"]:1, "W":-1, door["W"]:-1, "N":0, door["N"]:0, "S":0, door["S"]:0}
    dy = {"E":0, door["E"]:0, "W":0, door["W"]:0, "N":-1, door["N"]:-1, "S":1, door["S"]:1}
    opp = {"E":"W",
           "W":"E",
           "N":"S",
           "S":"N",
           door["E"]:door["W"],
           door["W"]:door["E"],
           door["N"]:door["S"],
           door["S"]:door["N"]} # opposite direction labels
    right = {"E":"S",
             "W":"N",
             "N":"E",
             "S":"W",
             door["E"]:door["S"],
             door["W"]:door["N"],
             door["N"]:door["E"],
             door["S"]:door["W"]} # right turn
    left = {"E":"N",
            "W":"S",
            "N":"W",
            "S":"E",
            door["E"]:door["N"],
            door["W"]:door["S"],
            door["N"]:door["W"],
            door["S"]:door["E"]} # left turn

    def __init__(self, width, height):
        self.width=width
        self.height=height
        self.grid = [[0 for n in range(width)] for m in range(height)]
        self.hunt_candidates = [[0 for n in range(width)] for m in range(height)]

    #-----------------------------------------------------------
    def get_doors(self, x, y):
        return self.grid[y][x]

    def has_door(self, x, y, door):
        return door & self.grid[y][x]

    def find_unvisited(self):
        result=[]
        for y,row in enumerate(self.grid):
            for x,cell in enumerate(row):
                if cell == 0:
                    result.append((x,y))
        return result

    def find_hunt_candidates(self):
        result=[]
        for y,row in enumerate(self.grid):
            for x,cell in enumerate(row):
                if cell == 0 and self.hunt_candidates[y][x]:
                    result.append((x,y))
        return result

    def visited(self, x, y):
        return self.grid[y][x] != 0

    def visited_neighbors(self, x, y):
        vis_nbrs = []
        for d in ("N","S","E","W"):
            nx = x+self.dx[d]
            ny = y+self.dy[d]
            if not self.out_of_bounds(nx, ny) and self.visited(nx, ny):
                vis_nbrs.append(d)
        return vis_nbrs

    def has_visited_neighbor(self, x, y):
        return len(self.visited_neighbors(x,y)) > 0

    def out_of_bounds(self, x, y):
        return (x<0) or (x>=self.width) or (y<0) or (y>=self.height)

    def connect(self, x, y, d):
        nx = x+self.dx[d]
        ny = y+self.dy[d]
        self.grid[y][x] |= self.door[d]
        self.grid[ny][nx] |= self.opp[self.door[d]]
        self.update_hunt_candidates(nx, ny)

    def update_hunt_candidates(self, x, y):
        for d in ("N", "S", "E", "W"):
            nx = x+self.dx[d]
            ny = y+self.dy[d]
            if not self.out_of_bounds(nx, ny):
                self.hunt_candidates[ny][nx] = True

    def total_cells(self):
        """ Total number of cells
        :return: Number of cells in maze
        """
        return self.width * self.height

    def unconnected_cells(self):
        """ Number of unconnected cells
        :return: Number of unconnected cells
        """
        return sum(sum(1 for c in row if c==0)
                   for row in self.grid)

    #------------------------------
    # Maze generation routine
    #
    def generate(self, inertia=0, progress_hook=None):
        x, y = 0, 0
        try:
            while True:
                self.walk(x,y, inertia)
                x,y = self.hunt()
                self.connect_hunted(x,y)
                if progress_hook is not None:
                    progress_hook(self.unconnected_cells())
        except DeadEnd:
            pass

        if progress_hook is not None:
            progress_hook(self.unconnected_cells())

    #------------------------------
    # Random walk routines
    #
    def _walk_step(self, cx, cy, last_dir=None, inertia=0):
        """One step in a random walk.

        Steps one step in a random direction from (cx,cy) in the grid,
        staying in bounds and avoiding visited squares. Returns the
        direction ("N","S","E","W") to the new square, or raises a
        DeadEnd exception if no move is possible.

        """
        dirs = ["N","S","E","W"]
        if last_dir is not None:
            dirs.remove(self.opp[last_dir])
            if inertia > 0:
                dirs.extend([last_dir]*inertia)
        random.shuffle(dirs)
        for d in dirs:
            nx = cx + self.dx[d]
            ny = cy + self.dy[d]

            if self.out_of_bounds(nx, ny) or self.visited(nx,ny):
                continue # out of bounds or already visited

            return d

        # tried all the directions without success
        raise DeadEnd()

    def walk(self, start_x, start_y, inertia=0):
        # walk until we get a DeadEnd exception
        cx=start_x
        cy=start_y
        d = None
        try:
            while True:
                d = self._walk_step(cx, cy, d, inertia)
                self.connect(cx, cy, d)
                cx += self.dx[d]
                cy += self.dy[d]
        except DeadEnd:
            return


    #------------------------------
    # Hunting Routine
    #
    def hunt(self):
        unvis = self.find_hunt_candidates()
        if len(unvis) == 0:
            raise DeadEnd()
        return random.choice(unvis)

    def connect_hunted(self, x, y):
        # connect to a random direction
        dirs = self.visited_neighbors(x,y)
        d = random.choice(dirs)
        self.connect(x,y,d)
        self.update_hunt_candidates(x, y)

