import logging
import subprocess

USE_TIMEOUT = False  # Not available on Windows, but keeps from waiting on the client forever


########################################################################
class ClientErrorException(Exception):
    ####################################################################
    def __init__(self, winner=None, loser=None, message=None):
        super(Exception, self).__init__()
        self.winner = winner
        self.loser = loser
        self.message = message

    ####################################################################
    def __str__(self):
        return self.message


########################################################################
class NullStream(object):
    ####################################################################
    def write(*args):
        pass

    ####################################################################
    def flush(*args):
        pass


########################################################################
class SimpleObserver(object):
    ####################################################################
    def __init__(self):
        self.out_file = file("observer.log", "w")

    ####################################################################
    def send(self, line):
        self.out_file.write(line)
        self.out_file.write("\n")

    ####################################################################
    def send_ship_locations(self, player_name, ship_locations):
        s = "|ship locations|%s|" % player_name
        s += "|".join((" ".join(ship) for ship in ship_locations))
        s += "|END|"
        self.send(s)

    ####################################################################
    def send_shots(self, player_name, player_shots):
        s = "|shots|%s|" % player_name
        s += "|".join((" ".join(shot) for shot in player_shots))
        s += "|END|"
        self.send(s)

    ####################################################################
    def set_players(self, player1_name, player2_name):
        s = "|players|%s|%s|END|" % (player1_name, player2_name)
        self.send(s)


########################################################################
class ClientProxy(object):
    def __init__(self, name, client):
        self.name = name
        self.client = client
        self.ships = []

    ####################################################################
    def send(self, line):
        line = line.strip() + "\n"
        logging.info("From Server to %s: %s" % (self.name, line.strip()))
        try:
            self.client.stdin.write(line)
            self.client.stdin.flush()
        except Exception, e:
            logging.error("error with sending to client (%s): %s" % (self.name, str(e)))
            raise ClientErrorException(loser=self.name, message="Exception sending to (%s)" % self.name)

    ####################################################################
    def receive(self):
        if USE_TIMEOUT:
            import timeout
            stdout_read = timeout.TimeoutFunction(self.client.stdout.readline, 10)
            try:
                return stdout_read().strip()
            except timeout.TimeoutFunctionException:
                logging.error("Client taking too long to respond (%s)" % self.name)
                raise ClientErrorException(loser=self.name, message="Client taking too long to respond (%s)" % self.name)
        else:
            return self.client.stdout.readline().strip()


#######################################################################
class Player(object):
    def __init__(self, name, popen_args, cwd):
        self.name = name
        self.popen_args = popen_args
        self.cwd = cwd

    ###################################################################
    def getClientProxy(self, other):
        s = subprocess.Popen(self.popen_args + [self.name, other.name], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.cwd)
        return ClientProxy(self.name, s)

#######################################################################
class NoisyPlayer(Player):
    def getClientProxy(self, other):
        s = subprocess.Popen(self.popen_args + [self.name, other.name], stdin=subprocess.PIPE, stdout=subprocess.PIPE, cwd=self.cwd)
        return ClientProxy(self.name, s)
