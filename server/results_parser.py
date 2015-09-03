TOTAL_ZERO = False

#######################################################################
def main():
    players = set()
    for line in file("results.txt"):
        player1, player2, result = line.split("\t")
        #result = int(result)
        players.add(player1)
        players.add(player2)

    ### I've got all players, generate the table
    grid = {}
    for name in players:
        grid[name] = {}
        for name2 in players:
            grid[name][name2] = 0

    ### now populate the table
    for line in file("results.txt"):
        player1, player2, result = line.split("\t")
        result = int(result)

        ### I have two different ways of showing the winner
        ### the first has where each loss counts as -1, and each win counts as 1
        ### so that all players totals sum up to 0.

        ### The other option is to only count wins, in which case all players
        ### totals sum up to the number of non-tie games.

        ### Basically, the first method highlights the differences between
        ### players more but disguises how many runs there were, while the
        ### second obscures the scores a little bit but preserves more
        ### information.
        if TOTAL_ZERO:
            grid[player1][player2] += result
            grid[player2][player1] -= result
        else:
            if result > 0:
                grid[player1][player2] += 1
            else:
                grid[player2][player1] += 1

    names = list(players)
    names.sort()

    ### write header
    out_file = file("results.csv", "w")
    out_file.write("\t")
    out_file.write("\t".join(names))
    out_file.write("\tTotal\n")

    ### now write rows
    for name in names:
        total = 0
        values = []
        for name2 in names:
            values.append(str(grid[name][name2]))
            total += grid[name][name2]
        out_file.write("%s\t%s\t%s\n" % (name, "\t".join(values), str(total)))

#######################################################################
main()
