import json
from typing import Dict


def get_exception(ex: Exception) -> str:
    return 'An exception of type {0} occurred. Arguments: {1!r}'.format(type(ex).__name__, ex.args)


def modify_environment(key, value) -> None:
    env = open('assets\\environment.json', 'r')
    json_object = json.load(env)
    env.close()

    json_object[key] = value

    env = open('assets\\environment.json', 'w')
    json.dump(json_object, env)
    env.close()


def get_environment(path) -> Dict:
    env = open(path, 'r')
    json_object = json.load(env)

    return dict(json_object)

