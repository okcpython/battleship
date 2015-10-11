from server_utils import Player


#######################################################################
def get_players():
    return {"human":  Player("Human",  ["python", "-u", "human.py"], "../client/human"),
            # "basic1": Player("Basic1", ["python", "-u", "really_simple_client.py"], "../client/python_sample"),
            "basic1": Player("Basic1", ["python", "-u", "simple_client.py"], "../client/python_sample"),
            "basic2": Player("Basic2", ["python", "-u", "simple_client.py"], "../client/python_sample")}
    # return {"human":  Player("Human",  ["python", "-u", "human.py"], "../client/human"),
    #         "frank_evans": Player("frank_evans", ["python", "-u", "battleship_frank.py"], "../client/frank_evans"),
    #         "ike_hall": Player("ike_hall", ["/usr/bin/python", "-u", "ikeclient.py"], "../client/ike_hall"),
    #         "major_tom": Player("major_tom", ["/home/tnance/projects/okcpython/battleship/client/major_tom/bin/local_ruby/bin/ruby", "bin/major_tom"], "../client/major_tom"),
    #         "mike_mattice": Player("mike_mattice", ["python", "-u", "twisted_client_v2.py"], "../client/mmattice")}
