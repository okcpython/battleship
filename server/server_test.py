import unittest
from server import BattleshipServer
from server_utils import ClientProxy, ClientErrorException, NullStream


########################################################################
class MockClient(object):
    ####################################################################
    def __init__(self):
        self.stdin = NullStream()
        self.stdout = NullStream()


########################################################################
class ServerTests(unittest.TestCase):
    ####################################################################
    def setUp(self):
        self.player1 = ClientProxy("p1", MockClient())
        self.player2 = ClientProxy("p2", MockClient())
        self.server = BattleshipServer(5, 5, [1, 1], self.player1, self.player2)

    ####################################################################
    def test_parse_line_into_value_sets(self):
        values = self.server.parse_line_into_value_sets("|RESPONSE|ship_locations|0 0 H|0 1 H|0 2 H|END|")
        self.assertEqual(values, [["0", "0", "H"], ["0", "1", "H"], ["0", "2", "H"]])

        values = self.server.parse_line_into_value_sets("|RESPONSE|shots|3 2|4 1|4 2|END|")
        self.assertEqual(values, [["3", "2"], ["4", "1"], ["4", "2"]])

    ####################################################################
    def test_overlapping_ships(self):
        self.server.get_player_info = lambda x, y: [["0", "0", "H"], ["0", "0", "H"]]
        with self.assertRaisesRegexp(ClientErrorException, "overlapping ships from client p1") as context:
            self.server.get_ships(self.player1)
        self.assertEqual(context.exception.winner, None)
        self.assertEqual(context.exception.loser, "p1")

    ####################################################################
    def test_ships_out_of_bounds(self):
        self.server.get_player_info = lambda x, y: [["10", "0", "H"], ["0", "0", "H"]]
        with self.assertRaisesRegexp(ClientErrorException, "ship out-of-bounds from client p1") as context:
            self.server.get_ships(self.player1)
        self.assertEqual(context.exception.winner, None)
        self.assertEqual(context.exception.loser, "p1")

    ####################################################################
    def test_client_gave_garbage_for_ship_placement(self):
        self.player2.client.stdout.readline = lambda: "asdfw\n"
        with self.assertRaisesRegexp(ClientErrorException, "bad line from client: \(asdfw\)") as context:
            self.server.get_ships(self.player2)
        self.assertEqual(context.exception.winner, None)
        self.assertEqual(context.exception.loser, "p2")

    ####################################################################
    def test_client_gave_garbage_for_shots(self):
        self.player1.client.stdout.readline = lambda : "asdfw\n"
        with self.assertRaisesRegexp(ClientErrorException, "bad line from client: \(asdfw\)") as context:
            self.server.get_player_shots(self.player1)
        self.assertEqual(context.exception.winner, None)
        self.assertEqual(context.exception.loser, "p1")

    ####################################################################
    def test_client_submitted_too_many_ships(self):
        self.server.get_player_info = lambda x, y: [["0", "0", "H"], ["1", "0", "H"], ["2", "0", "H"]]
        with self.assertRaisesRegexp(ClientErrorException, "incorrect number of ships from client p1") as context:
            self.server.get_ships(self.player1)
        self.assertEqual(context.exception.winner, None)
        self.assertEqual(context.exception.loser, "p1")

    ####################################################################
    def test_client_submitted_too_few_ships(self):
        self.server.get_player_info = lambda x, y: [["0", "0", "H"]]
        with self.assertRaisesRegexp(ClientErrorException, "incorrect number of ships from client p1") as context:
            self.server.get_ships(self.player1)
        self.assertEqual(context.exception.winner, None)
        self.assertEqual(context.exception.loser, "p1")

    ####################################################################
    def test_client_submitted_too_many_shots(self):
        self.server.get_num_surviving_ships = lambda x: 1
        self.server.get_player_info = lambda x, y: [["0", "0"], ["0", "1"], ["0", "2"], ["0", "3"], ["0", "4"], ["0", "5"]]
        with self.assertRaisesRegexp(ClientErrorException, "bad number of shots from client p1") as context:
            self.server.get_player_shots(self.player1)
        self.assertEqual(context.exception.winner, None)
        self.assertEqual(context.exception.loser, "p1")

    ####################################################################
    def test_client_submitted_fewer_shots(self):
        self.server.get_num_surviving_ships = lambda x: 2
        self.server.get_player_info = lambda x, y: [["0", "0"]]
        result = self.server.get_player_shots(self.player1)
        self.assertEqual(result, [(0, 0)])  # correctly parsed the result


########################################################################
if __name__ == "__main__":
    unittest.main()
