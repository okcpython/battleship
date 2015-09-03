import sys


#######################################################################
class ClientBase(object):
    name = "ClientBase"

    ####################################################################
    def __init__(self):
        self.num_ships = 0
        self.grid_width = 0
        self.grid_height = 0
        self.ship_sizes = None

    ###################################################################
    def run(self):
        while True:
            line = raw_input()
            assert(line.endswith("|END|"))
            if line == "|INFO|end game|END|":
                return
            elif line == "|QUERY|ship locations|END|":
                self.get_ship_locations()
            elif line.startswith("|QUERY|shots"):
                num_shots = int(line.split("|")[3])
                self.get_shots(num_shots)
            elif line.startswith("|INFO|grid size"):
                grid_size = line.split("|")[3].split()
                self.grid_width = int(grid_size[0])
                self.grid_height = int(grid_size[1])
            elif line.startswith("|INFO|num ships"):
                num_ships = line.split("|")[3]
                self.num_ships = int(num_ships)
            elif line.startswith("|INFO|ship sizes"):
                self.ship_sizes = [int(x) for x in line.split("|")[3:-2]]
            elif line.startswith("|INFO|"):
                pass
            else:
                sys.stderr.write("%s: Unknown incoming line: %s\n" % (self.name, line))
                return

    ###################################################################
    def get_ship_locations(self):
        raise NotImplementedError()

    ###################################################################
    def get_shots(self, num_shots):
        raise NotImplementedError()

    ###################################################################
    def send(self, tag, data):
        line = "|RESPONSE|%s|%s|END|\n" % (tag, data)
        sys.stdout.write(line)
