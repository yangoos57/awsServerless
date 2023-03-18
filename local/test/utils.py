import pickle


def write_pkl(item: str, dir: str = None):
    # store list in binary file so 'wb' mode
    with open(f"{dir}", "wb") as fp:
        pickle.dump(item, fp)
        print("Done writing list into a binary file")


def read_pkl(dir: str) -> list:
    # for reading also binary mode is important
    with open(dir, "rb") as fp:
        n_list = pickle.load(fp)
        return n_list
