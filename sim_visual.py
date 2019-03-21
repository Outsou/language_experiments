from server import get_server


if __name__ == "__main__":
    server = get_server(play_guessing=True, env_name='default', random_behaviour=True,
                        route_conceptualization='conceptualize', agents=4)
    server.port = 8521  # The default
    server.launch()
