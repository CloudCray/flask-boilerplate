from os import path
from my_flask_app import create_app

cur_dir = path.dirname(path.realpath(__file__))
env_file_name = path.join(cur_dir, "config", "env")
env_name = open(env_file_name).read().strip()

application = create_app(env_name)


if __name__ == "__main__":
    application.run()