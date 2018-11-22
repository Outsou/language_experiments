from server import get_server


if __name__ == "__main__":
    server = get_server(play_guessing=True)
    server.port = 8521  # The default
    server.launch()
