from server import get_server


if __name__ == "__main__":
    server = get_server(play_guessing=False, env_name='beer_only', random_behaviour=True)
    server.port = 8521  # The default
    server.launch()
