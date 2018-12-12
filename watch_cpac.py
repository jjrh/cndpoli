import argparse

#import lib
from lib import util
from lib.cpac import cpac




def print_cpac():
    for v in c:
        v.pretty_print()


def main(sleeptime=60,do_clear=False):
    while 1:
        if do_clear:
            CLEAR = '\033[1J'
        else:
            CLEAR="\n------------------------------------------------\n"
        print(CLEAR)

        c.load_header()
        c.update()
        print_cpac()
        util.print_countdown(sleeptime)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Watch for new CPAC events')
    parser.add_argument("-t",'--sleeptime', type=int, required=False, help="the amount of time we sleep before refreshing", default=60)
    parser.add_argument("--noresolve", action='store_true', required=False, help="Don't resolve the m3u8 urls, default false")
    parser.add_argument("--doclear", action='store_true', required=False, help="Clear the output every refresh, default false")
    parser.add_argument("--usecolors", type=util.str2bool, nargs='?',
                        const=True, default=True,
                        help="Use colors")
    args = parser.parse_args()
    c = cpac(**(vars(args)))
    main(args.sleeptime)
