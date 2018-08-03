from server import server


def start_visualization_server():
    server.port = 8521  # The default
    server.launch()


if __name__ == "__main__":
    start_visualization_server()
