from matplotlib import use
use('PDF')
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from argparse import ArgumentParser
from importlib import resources as importlib_resources
import papersize
from tqdm import tqdm
from .maze import Maze


class Plotter(object):
    def __init__(self,
                 mz,
                 tile_width=1, tile_height=1,
                 start_image=None,
                 end_image=None):
        self.maze = mz
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.start_image = start_image
        self.end_image = end_image

        # computed properties
        self.surf_width = self.maze.width * self.tile_width
        self.surf_height = self.maze.height * self.tile_height

        
    def plot_maze(self, ax):
        """Plot a maze."""
    
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])

        segments = self.generate_segments()
        
        with ProgressBar(desc="Simplifying", total=len(segments)) as prog_bar:
            self.simplify_segments(segments, prog_bar.update)
    
        segments.sort(key=lambda x:len(x))
    
        for seg in ProgressBar(segments, desc="Plotting walls"):
            x=[s[0] for s in seg]
            y=[s[1] for s in seg]
            ax.plot(x, y, 'k-')
        ax.set_xlim(-self.tile_width,self.surf_width+self.tile_width)
        ax.set_ylim(self.surf_height+self.tile_height, -self.tile_height)
    
        if self.start_image is not None:
            img_width=self.start_image.shape[0]
            img_height=self.start_image.shape[1]
            zoom=50*min(abs(float(self.tile_width)/img_width),
                        abs(float(self.tile_height)/img_height))
            #print img_width, zoom
            ax.add_artist(AnnotationBbox(OffsetImage(self.start_image,
                                                     zoom=zoom),
                                         (self.tile_width*0.5, self.tile_height*0.5),
                                         frameon=False))
        if self.end_image is not None:
            img_width=self.end_image.shape[0]
            img_height=self.end_image.shape[1]
            zoom=50*min(abs(float(self.tile_width)/img_width),
                        abs(float(self.tile_height)/img_height))
            #print img_width, zoom
            ax.add_artist(AnnotationBbox(OffsetImage(self.end_image,
                                                     zoom=zoom),
                                         (self.surf_width-self.tile_width*0.5, self.surf_height-self.tile_height*0.5),
                                         frameon=False))
    #    ax.text(self.surf_width-0.5*self.tile_width, self.surf_height-0.5*self.tile_height, "End",
    #            ha='center', va='center', size='smaller')

    def generate_segments(self):
        segments = []
        with ProgressBar(desc="Generating walls",
                         total=self.maze.height + self.maze.width - 2,
                         mode="increment") as prog_bar:
            # plot horizontal lines (no need to plot top line---that is
            # the border)
            for y in range(1, self.maze.height):
                prog_bar.update()
                x0 = 0
                line_active = False
                for x in range(0, self.maze.width):
                    if (self.maze.grid[y][x] & self.maze.door["N"]) == 0:
                        # no door North; be sure a line is started
                        line_active = True
                    else:
                        # door North; draw a line if needed
                        if line_active:
                            segments.append([(x0 * self.tile_width, y * self.tile_height),
                                             (x * self.tile_width, y * self.tile_height)])
                            line_active = False
                        x0 = x + 1
                if line_active:
                    segments.append([(x0 * self.tile_width, y * self.tile_height),
                                     (self.surf_width, y * self.tile_height)])

            # plot vertical lines (no need to plot left line---that is
            # the border)
            for x in range(1, self.maze.width):
                prog_bar.update()
                y0 = 0
                line_active = False
                for y in range(0, self.maze.height):
                    if (self.maze.grid[y][x] & self.maze.door["W"]) == 0:
                        # no door West; be sure a line is started
                        line_active = True
                    else:
                        # door West; draw a line if needed
                        if line_active:
                            segments.append([(x * self.tile_width, y0 * self.tile_height),
                                             (x * self.tile_width, y * self.tile_height)])
                            line_active = False
                        y0 = y + 1
                if line_active:
                    segments.append([(x * self.tile_width, y0 * self.tile_height),
                                     (x * self.tile_width, self.surf_height)])

        segments.append([(0, 0), (self.surf_width, 0)])
        segments.append([(self.surf_width, 0), (self.surf_width, self.surf_height)])
        segments.append([(0, 0), (0, self.surf_height)])
        segments.append([(0, self.surf_height), (self.surf_width, self.surf_height)])
        return segments

    def simplify_segments(self, s, progress_hook=None):
        """Reduce the number of individual lines."""
        ii = 0
        max_ii = 0
        while ii < len(s):
            if (ii > max_ii):
                progress_hook(len(s) - max_ii)
                max_ii = ii
            starts = [seg[0] for seg in s]
            ends = [seg[-1] for seg in s]

            this_start = s[ii][0]
            this_end = s[ii][-1]
            try:
                jj = starts.index(this_end)  # finds first match
                if ii == jj:
                    raise ValueError()
                s[ii].extend(s[jj][1:])
                starts.pop(jj)
                ends.pop(jj)
                s.pop(jj)
                ii = 0
                continue
            except ValueError:
                pass

            # match end to start
            try:
                jj = ends.index(this_start)  # finds first match
                if ii == jj:
                    raise ValueError()
                s[ii] = s[jj] + s[ii][1:]
                starts.pop(jj)
                ends.pop(jj)
                s.pop(jj)
                ii = 0
                continue
            except ValueError:
                pass

            # match start to start
            try:
                # don't match self
                jj = ii + 1 + starts[ii + 1:].index(this_start)  # finds first match
                s[ii].reverse()
                s[ii].extend(s[jj][1:])  # reverse one of them
                starts.pop(jj)
                ends.pop(jj)
                s.pop(jj)
                ii = 0
                continue
            except ValueError:
                pass

            # match end to end
            try:
                # don't match self
                jj = ii + 1 + ends[ii + 1:].index(this_end)  # finds first match
                s[ii].extend(s[jj][::-1])
                starts.pop(jj)
                ends.pop(jj)
                s.pop(jj)
                ii = 0
                continue
            except ValueError:
                ii += 1

        progress_hook(0)


def parse_maze_size(s):
    """Parse a maze size string into a tuple

    Takes a string of either "N" or "NxM" and converts it into a 2-element
    tuple with integer elements indicating (width, height).

    :param s: string to parse
    :return: 2-element tuple, (width, height)
    """
    dims = s.lower().split("x")
    if len(dims) == 1:
        w = dims[0]
        h = w
    elif len(dims) == 2:
        (w, h) = dims
    else:
        raise ValueError("Expected string like 'n' or 'n x m'")

    return (int(w), int(h))

def parse_paper_size(s):
    """Parse a paper size into a tuple

    Parses a paper size or description (like 'letter') and returns a tuple
    of (width, height) in inches.

    :param s: string to parse
    :return: 2-element tuple, (width, height) in inches
    """
    (w,h) = papersize.parse_papersize(s, 'in')
    return [float(w), float(h)]  # instead of Decimal

def parse_margin(s):
    """Parse a margin specification
    :param s: string to parse
    :return: 4-element tuple, with (left, right, top, bottom) margins in inches
    """
    margins = s.split(',')
    if len(margins) == 1:
        left = papersize.parse_length(margins[0], 'in')
        right = left
        top = left
        bottom = left
    elif len(margins) == 2:
        left = papersize.parse_length(margins[0], 'in')
        right = left
        top = papersize.parse_length(margins[1], 'in')
        bottom = top
    elif len(margins) == 4:
        left = papersize.parse_length(margins[0], 'in')
        right = papersize.parse_length(margins[1], 'in')
        top = papersize.parse_length(margins[2], 'in')
        bottom = papersize.parse_length(margins[3], 'in')
    else:
        raise ValueError("Expected 1, 2, or 4 margin specifications")

    return [float(x) for x in (left, right, top, bottom)]

def margins_to_scale(left, right, top, bottom, width, height):
    """Convert linear margins to matplotlib axis scale

    Units are arbitrary, but must be the same for all input values

    :param left: left margin
    :param right: right margin
    :param top: top margin
    :param bottom: bottom margin
    :param width: width of the figure
    :param height: height of the figure
    :return: Scale tuple for use with add_axis()
    """
    return [float(left)/width,
            float(bottom) / height,
            float(width-left-right)/width,
            float(height - top - bottom) / height]

class ProgressBar(tqdm):
    """ Progress bar updated by number of items remaining
    """
    desc_width = None

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("mode", "countdown")
        self.mode=kwargs["mode"]
        del(kwargs["mode"])

        if "desk" in kwargs:
            kwargs['desc'] = self._fix_desc_width(kwargs['desc'])

        kwargs.setdefault("bar_format", "{l_bar}{bar}") # change the default
        kwargs.setdefault("leave", False)
        super(ProgressBar, self).__init__(*args, **kwargs)

    def _fix_desc_width(self, desc):
        w = ProgressBar.desc_width
        if (w is not None) and (len(desc) < w):
            return desc + " "*(w - len(desc))
        return desc

    def update(self, n=1):
        if self.mode=="countdown":
            # In countdown mode, n is the number of iterations left
            n = self.total - n - self.n
        elif self.mode=="increment":
            # In increment mode, n is the number of iterations completed since
            # the last cal (i.e., the tqdm default)
            pass
        else:
            raise ValueError("Unknown mode ({:s})".format(self.mode))

        return super(ProgressBar, self).update(n)


def main():
    ProgressBar.desc_width = 16

    parser = ArgumentParser(description="Randomly generate a maze.")
    parser.add_argument("--maze-size", "-s",
                        type=parse_maze_size,
                        dest="maze_size",
                        default="15x15",
                        help="Number of tiles in each direction as 'width x height' "
                             "Default = %(default)s")
    parser.add_argument("--paper-size", "-p",
                        type=parse_paper_size,
                        dest="paper_size",
                        default="letter",
                        help="Paper size for output (e.g., '8.5in x 11in', 'A4'). "
                             "If dimensions are given, units default to points "
                             "if not specified. Default = %(default)s")
    parser.add_argument("--margins", "-m",
                        type=parse_margin,
                        dest="margins",
                        default="0.5in",
                        help="Margin to leave around the maze, either as a single length "
                             "to apply on all sides, 'h,v' for distinct horizontal and vertical "
                             "margins, or 'l,r,t,b' for distinct left, right, top, and bottom "
                             "margins. Default = %(default)s")
    parser.add_argument("--inertia", "-i", type=int, dest="inertia", default=0)
    parser.add_argument("--num", "-n",
                        type=int,
                        dest="num",
                        default=1,
                        help="Number of mazes to generate. Output will be a PDF with one "
                             "maze per page. Default = %(default)s")
    parser.add_argument("--seed", type=int, dest="seed", default=None)
    args=parser.parse_args()

    if args.seed is not None:
        import random
        random.seed(args.seed)

    plt.xkcd()
    pp=PdfPages('maze.pdf')

    print(f"Yurp: {args.paper_size} ({repr(args.paper_size)}")
    for nn in ProgressBar(range(args.num),
                          desc="Generating mazes",
                          bar_format="{l_bar} Completed {n_fmt}/{total_fmt} at {rate_fmt}",
                          leave=True,
                          unit="mazes"):
        mz = Maze(*args.maze_size)
        with ProgressBar(total=mz.total_cells(),
                         desc="Generating maze") as prog_bar:
            mz.generate(args.inertia,
                        lambda n_left: prog_bar.update(n_left))

        fig = plt.figure(figsize=args.paper_size, dpi=300)
        ax = fig.add_axes(
            margins_to_scale(*(args.margins + args.paper_size)),
            frameon=False)

        plotter = Plotter(
            mz,
            start_image=plt.imread(
                importlib_resources.files("maze.resources.images").joinpath(
                    "smiley.png"
                )
            ),
            end_image=plt.imread(
                importlib_resources.files("maze.resources.images").joinpath(
                    "target.png"
                )
            ),
        )
        plotter.plot_maze(ax)
        pp.savefig(fig)
    pp.close()

if __name__ == '__main__':
    main()
