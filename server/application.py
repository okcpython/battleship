import sys
import server
import players

NUM_ROUNDS = 100


#######################################################################
def run_two_clients(name1, name2):
    all_players = players.get_players()
    player1 = all_players[name1]
    player2 = all_players[name2]

    s = server.BattleshipServer(10, 10, [2, 3, 3, 4, 5], player1.getClientProxy(player2), player2.getClientProxy(player1))
    winner = s.run()
    print "winner:", winner


########################################################################
def run_all_clients():
    out_file = file("results.txt", "w")
    all_players = players.get_players()
    if "human" in all_players:  # Don't include the human client in our multi-round run
        del all_players["human"]
    all_players = all_players.values()
    # Start with the number of ties set to 0, then add each player with a zero score
    wins = {None: 0}
    for player in all_players:
        wins[player.name] = 0
    for i in range(len(all_players)):
        for j in range(i+1, len(all_players)):
            player1 = all_players[i]
            player2 = all_players[j]

            print ".",
            for round in range(NUM_ROUNDS):
                winner = None
                s = server.BattleshipServer(10, 10, [2, 3, 3, 4, 5], player1.getClientProxy(player2), player2.getClientProxy(player1))
                winner = s.run()
                wins[winner] += 1
                x = 0
                if winner == player1.name:
                    x = 1
                elif winner == player2.name:
                    x = -1
                out_file.write("%s\t%s\t%d\n" % (player1.name, player2.name, x))
                out_file.flush()
                s.player1.client.stdin.close()
                s.player1.client.stdout.close()
                if s.player1.client.stderr:
                    s.player1.client.stderr.close()
                s.player2.client.stdin.close()
                s.player2.client.stdout.close()
                if s.player2.client.stderr:
                    s.player2.client.stderr.close()
                s.player1.client.kill()
                s.player2.client.kill()

    print ""
    print "scores:"
    for key, value in wins.items():
        print key, ":", value
    out_file.close()


########################################################################
if __name__ == "__main__":
    if len(sys.argv) > 1:
        print "Running two clients..."
        run_two_clients(sys.argv[1], sys.argv[2])
    else:
        print "Running all clients..."
        run_all_clients()
