from client_base import ClientBase


#######################################################################
class SimpleClient(ClientBase):
    name = "SimpleClient"

    ####################################################################
    def __init__(self):
        super(SimpleClient, self).__init__()

        # location of next shot to make
        self.shooting_x = 0
        self.shooting_y = 0

    ###################################################################
    def get_ship_locations(self):
        locations = []
        for y in range(self.num_ships):
            locations.append("{x} {y} {orientation}".format(x=0, y=y, orientation="H"))
        str_locations = "|".join(locations)
        self.send("ship locations", str_locations)

    ###################################################################
    def get_shots(self, num_shots):
        shots = []
        for i in range(num_shots):
            shots.append("{x} {y}".format(x=self.shooting_x, y=self.shooting_y))
            self.shooting_x += 1
            if self.shooting_x == self.grid_width:
                self.shooting_x = 0
                self.shooting_y += 1
        str_shots = "|".join(shots)
        self.send("shots", str_shots)


#######################################################################
if __name__ == "__main__":
    SimpleClient().run()
