import sys
TOTAL_ZERO = False


########################################################################
def make_empty_results(names):
    grid = {}
    for name in names:
        grid[name] = {}
        for name2 in names:
            grid[name][name2] = 0
    return grid


########################################################################
def print_grid(grid, names):
    row_template = "{:>15}" * (len(names) + 2)
    header_data = [""] + names + ["Total"]
    print row_template.format(*header_data)
    for name in names:
        row_data = []
        total = 0
        row_data.append(name)
        for name2 in names:
            if name2 == name:
                row_data.append("--")
            else:
                val = grid[name][name2]
                total += val
                row_data.append(val)
        row_data.append(total)
        print row_template.format(*row_data)

#######################################################################
def main():
    players = set()
    for line in file(sys.argv[1]):
        player1, player2, result = line.split("\t")
        #result = int(result)
        players.add(player1)
        players.add(player2)

    ### I've got all players, generate the table
    grid_wins = make_empty_results(players)
    grid_zero = make_empty_results(players)

    ### now populate the table
    for line in file(sys.argv[1]):
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
        grid_zero[player1][player2] += result
        grid_zero[player2][player1] -= result
        if result > 0:
            grid_wins[player1][player2] += 1
        else:
            grid_wins[player2][player1] += 1

    names = list(players)
    names.sort()
    print "\nJUST WINS:"
    print_grid(grid_wins, names)
    print ""
    print "-" * ((len(names) + 2) * 15)
    print "\nWINS AND LOSSES:"
    print_grid(grid_zero, names)
    print ""


#######################################################################
if __name__ == "__main__":
    main()
