import time
import sys
import datetime


def str2bool(v):
    import argparse
    # Snagged from https://stackoverflow.com/a/43357954
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')



class tdelta:
    def __init__(self,t1,t2):
        self.t1 = t1
        self.t2 = t2

        if(t1 > t2):
            self.td = t1-t2
        else:
            self.td = t2-t1

        self.hours = self.td.seconds//3600
        self.minutes = (self.td.seconds//60)%60
        self.seconds = self.td.seconds % 60

        self.H = self.hours
        self.M = self.minutes
        self.S = self.seconds

        self.h = self.hours
        self.m = self.minutes
        self.s = self.seconds

    def format(self,fmt):
        fmt = fmt.replace("%H",'{0:02d}'.format(self.H))
        fmt = fmt.replace("%M",'{0:02d}'.format(self.M))
        fmt = fmt.replace("%S",'{0:02d}'.format(self.S))
        return fmt

    def __str__(self):
        return("%s:%s:%s" % ('{0:02d}'.format(self.H),'{0:02d}'.format(self.M),'{0:02d}'.format(self.S)))


def print_countdown(length):
    c = length
    while c >= 0:
        sys.stdout.write('\033[K')
        sys.stdout.flush()
        sys.stdout.write(('\033[1000Dupdate in: %s' % (c)))
        sys.stdout.flush()
        c-=1
        time.sleep(1)
    print("")

def unix_to_datetime(inp):
    return datetime.datetime.fromtimestamp(int(inp))

def time_from_now(tin):
    return tdelta(tin,datetime.datetime.now())

def get_timedelta(tin):
    td = tin-datetime.datetime.now()
    return { 'h': td.seconds//3600,
             'm': (td.seconds//60)%60 }

    #return "%s:%s" % (td.seconds//3600, (td.seconds//60)%60)


def print_countdown(length):
    c = length
    while c >= 0:
        sys.stdout.write('\033[K')
        sys.stdout.flush()
        sys.stdout.write(('\033[1000Dupdate in: %s' % (c)))
        sys.stdout.flush()
        c-=1
        time.sleep(1)
    print("")
