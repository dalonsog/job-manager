from jobmanager.core.db import get_engine, init_db


if __name__ == "__main__":
    init_db(get_engine())
