from server_utils import Player


#######################################################################
def get_players():
    return {"human":  Player("Human",  ["python", "-u", "human.py"], "../client/human"),
            # "basic1": Player("Basic1", ["python", "-u", "really_simple_client.py"], "../client/python_sample"),
            "basic1": Player("Basic1", ["python", "-u", "simple_client.py"], "../client/python_sample"),
            "basic2": Player("Basic2", ["python", "-u", "simple_client.py"], "../client/python_sample")}
