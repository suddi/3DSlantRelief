from subprocess import Popen, PIPE

from settings import INCLINOMETER


class Inclinometer(object):

    def __init__(self):
        self.process = Popen(INCLINOMETER, stdin=PIPE, stdout=PIPE)

    def get_serial_number(self):
        self.process.stdin.write('getSerialNumber\n')
        return int(self.process.stdout.readline().rstrip('\n'))

    def get_X(self):
        self.process.stdin.write('getX\n')
        return float(self.process.stdout.readline().rstrip('\n'))

    def get_Y(self):
        self.process.stdin.write('getY\n')
        return float(self.process.stdout.readline().rstrip('\n'))

    def get_offset_X(self):
        self.process.stdin.write('getOffsetX\n')
        return float(self.process.stdout.readline().rstrip('\n'))

    def set_offset_X(self):
        self.process.stdin.write('setOffsetX\n')
        return int(self.process.stdout.readline().rstrip('\n'))

    def reset_offset_X(self):
        self.process.stdin.write('resetOffsetX\n')
        return int(self.process.stdout.readline().rstrip('\n'))

    def get_offset_Y(self):
        self.process.stdin.write('getOffsetY\n')
        return float(self.process.stdout.readline().rstrip('\n'))

    def set_offset_Y(self):
        self.process.stdin.write('setOffsetY\n')
        return int(self.process.stdout.readline().rstrip('\n'))

    def reset_offset_Y(self):
        self.process.stdin.write('resetOffsetY\n')
        return int(self.process.stdout.readline().rstrip('\n'))

    def close(self):
        self.process.stdin.write('quit\n')
        self.process.terminate()
