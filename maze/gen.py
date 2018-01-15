from matplotlib import use
use('PDF')
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from argparse import ArgumentParser
from pkg_resources import resource_stream
import papersize
import maze


def plot_maze(ax, mz, start_image=None, end_image=None):
    """Plot a maze."""

    def _simplify_segments(s):
        """Reduce the number of individual lines."""
        ii=0
        while ii < len(s):
            starts=[seg[0] for seg in s]
            ends=[seg[-1] for seg in s]

            this_start=s[ii][0]
            this_end=s[ii][-1]
            try:
                jj=starts.index(this_end) # finds first match
                if ii==jj:
                    raise ValueError()
                s[ii].extend(s[jj][1:])
                starts.pop(jj)
                ends.pop(jj)
                s.pop(jj)
                ii=0
                continue
            except ValueError:
                pass

            # match end to start
            try:
                jj=ends.index(this_start) # finds first match
                if ii==jj:
                    raise ValueError()
                s[ii]=s[jj]+s[ii][1:]
                starts.pop(jj)
                ends.pop(jj)
                s.pop(jj)
                ii=0
                continue
            except ValueError:
                pass

            # match start to start
            try:
                # don't match self
                jj=ii+1+starts[ii+1:].index(this_start) # finds first match
                s[ii].reverse()
                s[ii].extend(s[jj][1:]) # reverse one of them
                starts.pop(jj)
                ends.pop(jj)
                s.pop(jj)
                ii=0
                continue
            except ValueError:
                pass

            # match end to end
            try:
                # don't match self
                jj=ii+1+ends[ii+1:].index(this_end) # finds first match
                s[ii].extend(s[jj][::-1])
                starts.pop(jj)
                ends.pop(jj)
                s.pop(jj)
                ii=0
                continue
            except ValueError:
                ii+=1

    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])

    tile_width = 1
    tile_height = -1
    surf_width=mz.width*tile_width
    surf_height=mz.height*tile_height

    segments = []
    # plot horizontal lines (no need to plot top line---that is
    # the border)
    for y in range(1,mz.height):
        x0 = 0
        line_active = False
        for x in range(0, mz.width):
            if (mz.grid[y][x] & mz.door["N"]) == 0:
                # no door North; be sure a line is started
                line_active = True
            else:
                # door North; draw a line if needed
                if line_active:
                    segments.append( [(x0*tile_width, y*tile_height),
                                      (x*tile_width, y*tile_height)] )
                    line_active = False
                x0 = x+1
        if line_active:
            segments.append( [(x0*tile_width, y*tile_height),
                              (surf_width, y*tile_height)] )

    # plot vertical lines (no need to plot left line---that is
    # the border)
    for x in range(1,mz.width):
        y0 = 0
        line_active = False
        for y in range(0, mz.height):
            if (mz.grid[y][x] & mz.door["W"]) == 0:
                # no door West; be sure a line is started
                line_active = True
            else:
                # door West; draw a line if needed
                if line_active:
                    segments.append( [(x*tile_width, y0*tile_height),
                                      (x*tile_width, y*tile_height)] )
                    line_active = False
                y0 = y+1
        if line_active:
            segments.append( [(x*tile_width, y0*tile_height),
                              (x*tile_width, surf_height)] )

    segments.append( [(0, 0), (surf_width, 0)] )
    segments.append( [(surf_width, 0), (surf_width, surf_height)] )
    segments.append( [(0, 0), (0, surf_height)] )
    segments.append( [(0, surf_height), (surf_width, surf_height)] )

    _simplify_segments(segments)
    segments.sort(key=lambda x:len(x))

    for seg in segments:
        x=[s[0] for s in seg]
        y=[s[1] for s in seg]
        ax.plot(x, y, 'k-')
    ax.set_xlim(-tile_width,surf_width+tile_width)
    ax.set_ylim(surf_height+tile_height, -tile_height)

    if start_image is not None:
#        plt.imshow(start_image, extent=(0,tile_width,
#                                        tile_height, 0))
        img_width=start_image.shape[0]
        img_height=start_image.shape[1]
        zoom=50*min(abs(float(tile_width)/img_width),
                 abs(float(tile_height)/img_height))
        #print img_width, zoom
        ax.add_artist(AnnotationBbox(OffsetImage(start_image,
                                                 zoom=zoom),
                                     (tile_width*0.5, tile_height*0.5),
                                     frameon=False))
    if end_image is not None:
        img_width=end_image.shape[0]
        img_height=end_image.shape[1]
        zoom=50*min(abs(float(tile_width)/img_width),
                 abs(float(tile_height)/img_height))
        #print img_width, zoom
        ax.add_artist(AnnotationBbox(OffsetImage(end_image,
                                                 zoom=zoom),
                                     (surf_width-tile_width*0.5, surf_height-tile_height*0.5),
                                     frameon=False))
#    ax.text(surf_width-0.5*tile_width, surf_height-0.5*tile_height, "End",
#            ha='center', va='center', size='smaller')

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
    return map(float, [w, h]) # instead of Decimal

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

    return map(float, (left, right, top, bottom))

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

def main():
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
    parser.add_argument("--margin", "-m",
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
    for nn in range(args.num):
        mz = maze.Maze(*args.maze_size)
        mz.generate(args.inertia)

        fig = plt.figure(figsize=args.paper_size, dpi=300)
        ax = fig.add_axes(
            margins_to_scale(*(args.margins + args.paper_size)),
            frameon=False)

        plot_maze(ax, mz,
                  plt.imread(resource_stream('maze.resources.images', 'smiley.png')),
                  plt.imread(resource_stream('maze.resources.images', 'target.png')))

        #ax.set_xlim(-0.005, 1.005)
        #ax.set_ylim(-0.005, 1.005)

        pp.savefig(fig)
    pp.close()

if __name__ == '__main__':
    main()
