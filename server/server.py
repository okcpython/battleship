import logging
import logging.config
from server_utils import ClientErrorException, SimpleObserver

logging.config.fileConfig("logger.config")


#########################################################################
class BattleshipServer(object):
    def __init__(self, width, height, ship_sizes, player1, player2):
        self.width = width
        self.height = height
        self.player1 = player1
        self.player2 = player2
        self.players = [self.player1, self.player2]
        self.ship_sizes = ship_sizes
        self.observer = SimpleObserver()
        self.observer.set_players(player1.name, player2.name)
        logging.info("*" * 80)
        logging.info("board size:%d x %d" % (self.width, self.height))
        logging.info("ship sizes: %s" % (str(self.ship_sizes)))

    ####################################################################
    def run(self):
        game_over = False
        try:
            ### get ship placement
            self.send_all_clients("|INFO|grid size|%d %d|END|" % (self.width, self.height))
            self.observer.send("|grid size|%d %d|END|" % (self.width, self.height))
            self.send_all_clients("|INFO|num ships|%d|END|" % len(self.ship_sizes))
            self.observer.send("|num ships|%d|END|" % len(self.ship_sizes))
            str_ship_sizes = "|".join([str(x) for x in self.ship_sizes])
            self.send_all_clients("|INFO|ship sizes|%s|END|" % str_ship_sizes)
            self.observer.send("|ship sizes|%s|END|" % str_ship_sizes)

            self.get_ships(self.player1)
            self.get_ships(self.player2)

            ### start game loop
            while not game_over:
                game_over = self.play_round()
        except ClientErrorException, e:
            if e.winner:
                game_over = e.winner
            elif e.loser:
                game_over = self.other_player_name(e.loser)
            self.report_winner(game_over == self.player1.name, game_over == self.player2.name)
        if game_over == True:
            game_over = None
        self.end_game()
        return game_over

    ####################################################################
    def play_round(self):
        player_1_shots = self.get_player_shots(self.player1)
        player_2_shots = self.get_player_shots(self.player2)

        ### make shots
        self.play_shots(self.player1, self.player2, player_1_shots)
        self.play_shots(self.player2, self.player1, player_2_shots)

        ### check player status
        player_1_alive = self.check_player_alive(self.player1)
        player_2_alive = self.check_player_alive(self.player2)

        if player_1_alive and player_2_alive:
            return False
        else:
            return self.report_winner(player_1_alive, player_2_alive)

    ####################################################################
    def report_winner(self, player_1_alive, player_2_alive):
        if player_1_alive and not player_2_alive:
            self.player1.send("|INFO|won game|END|")
            self.player2.send("|INFO|lost game|END|")
            self.observer.send("|end game|%s won|END|" % self.player1.name)
            logging.info("%s won the game" % self.player1.name)
            return self.player1.name
        elif player_2_alive and not player_1_alive:
            self.player2.send("|INFO|won game|END|")
            self.player1.send("|INFO|lost game|END|")
            logging.info("%s won the game" % self.player2.name)
            self.observer.send("|end game|%s won|END|" % self.player2.name)
            return self.player2.name
        elif player_1_alive is False and player_2_alive is False:
            self.send_all_clients("|INFO|tie game|END|")
            logging.info("The game was tied")
            self.observer.send("|end game|tie game|END|")
            return True

    ####################################################################
    def get_player_info(self, player, tag):
        line = player.receive()
        logging.info("%s: %s", player.name, line)

        if not (line.startswith("|RESPONSE|" + tag + "|") and line.endswith("|END|")):
            logging.error("bad line from client: (%s)", line)
            raise ClientErrorException(loser=player.name, message="bad line from client: (%s)" % line)
        return self.parse_line_into_value_sets(line)

    ####################################################################
    def parse_line_into_value_sets(self, line):
        out_values = []
        items = line.split("|")[3:-2]
        for item in items:
            out_values.append(item.split())
        return out_values

    ####################################################################
    def get_ships(self, player):
        player.send("|QUERY|ship locations|END|")
        ship_locations = self.get_player_info(player, "ship locations")
        if len(ship_locations) != len(self.ship_sizes):
            logging.error("incorrect number of ships from client %s: Expected %d but got %d (%s)", player.name, len(self.ship_sizes), len(ship_locations), ship_locations)
            raise ClientErrorException(loser=player.name, message="incorrect number of ships from client %s: (%s)" % (player.name, str(ship_locations)))

        self.observer.send_ship_locations(player.name, ship_locations)
        ships = []
        used_locations = set()
        for index, (x, y, orientation) in enumerate(ship_locations):
            x = int(x)
            y = int(y)
            horizontal = orientation == "H"

            ### expand each ship into an array
            size = self.ship_sizes[index]
            ship = {}
            for size_index in range(size):
                ship[x, y] = True
                if (x, y) in used_locations:
                    ### already used spot
                    logging.error("overlapping ships from client %s: (%s)", player.name, ship_locations)
                    raise ClientErrorException(loser=player.name, message="overlapping ships from client %s: (%s)" % (player.name, str(ship_locations)))
                if not (0 <= x < self.width) or not (0 <= y < self.height):
                    logging.error("ship out-of-bounds from client %s: (%s)", player.name, ship_locations)
                    raise ClientErrorException(loser=player.name, message="ship out-of-bounds from client %s: (%s)" % (player.name, str(ship_locations)))

                used_locations.add((x, y))
                if horizontal:
                    x += 1
                else:
                    y += 1
            ships.append(ship)
        player.ships = ships

    ####################################################################
    def get_player_shots(self, player):
        num_shots_allowed = self.get_num_surviving_ships(player)
        player.send("|QUERY|shots|%d|END|" % num_shots_allowed)
        player_shots = self.get_player_info(player, "shots")
        self.observer.send_shots(player.name, player_shots)
        if len(player_shots) > num_shots_allowed:
            logging.error("bad number of shots from client %s: Expected %d but got %d (%s)", player.name, num_shots_allowed, len(player_shots), player_shots)
            raise ClientErrorException(loser=player.name, message="bad number of shots from client %s: (%s)" % (player.name, str(player_shots)))
        try:
            player_shots = [(int(x), int(y)) for (x, y) in player_shots]
        except:
            logging.error("bad line from client %s: (%s)", player.name, player_shots)
            raise ClientErrorException(loser=player.name, message="bad line from client %s: (%s)" % (player.name, str(player_shots)))
        return player_shots

    ####################################################################
    def other_player_name(self, player_name):
        """Simple way to get the name of the opponent given a player"""
        if player_name == self.player1.name:
            return self.player2.name
        else:
            return self.player1.name

    ####################################################################
    def play_shots(self, shooting_player, shot_at_player, shots):
        for location in shots:
            for ship in shot_at_player.ships:
                if location in ship:
                    logging.info("%s shot %s at (%d, %d)" % (shooting_player.name, shot_at_player.name, location[0], location[1]))
                    shot_at_player.send("|INFO|opponent hit|%d %d|END|" % location)
                    shooting_player.send("|INFO|you hit|%d %d|END|" % location)
                    ship[location] = False
                    break
            else:
                logging.info("%s misses %s at (%d, %d)" % (shooting_player.name, shot_at_player.name, location[0], location[1]))
                shot_at_player.send("|INFO|opponent miss|%d %d|END|" % location)
                shooting_player.send("|INFO|you miss|%d %d|END|" % location)

    ####################################################################
    def get_num_surviving_ships(self, player):
        count = 0
        for ship in player.ships:
            if any(ship.values()):
                count += 1
        return count

    ####################################################################
    def check_player_alive(self, player):
        return self.get_num_surviving_ships(player) > 0

    ####################################################################
    def send_all_clients(self, line):
        logging.info(line)
        for c in self.players:
            c.send(line)

    ####################################################################
    def end_game(self):
        try:
            self.send_all_clients("|INFO|end game|END|")
        except:
            pass
        logging.shutdown()
