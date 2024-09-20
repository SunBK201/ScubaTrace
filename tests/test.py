import sys

sys.path.append('..')

import scubatrace


def main():
    a_proj = scubatrace.CProject("../tests")
    print(a_proj.files[0].structs[0].name)


if __name__ == '__main__':
    main()
