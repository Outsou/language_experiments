from coopa_model import CoopaModel
from server import server


def start_visualization_server():
    server.port = 8521  # The default
    server.launch()


def test2():
    print('Running Test2...')
    model = CoopaModel(1, 60, 60, agent_type='coopa')
    for i in range(20):
        model.step()

    plot_cells(model)
    plot_wealth(model)


if __name__ == "__main__":
    start_visualization_server()
    # test2()
