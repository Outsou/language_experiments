import inspect
import environments

def get_env_cls(env_name):
    clss = [m[1] for m in inspect.getmembers(environments, inspect.isclass) if m[1].__module__ == 'environments']
    env_cls = None
    for cls in clss:
        if cls.name == env_name:
            env_cls = cls
            break
    assert env_cls is not None, 'No environment found with given name.'
    return env_cls

def create_env(env_name, model):
    env_cls = get_env_cls(env_name)
    return_val = env_cls.create_env(model)
    return return_val