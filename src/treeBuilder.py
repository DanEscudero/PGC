import sys
from Node import Node
from util import list_subcategories, parse_args

# Defaults
DEFAULT_QUERY_LEVEL = 3
DEFAULT_QUERY_PARAMETER = 'Mathematics'
DEFAULT_QUERY_PARAMETER = 'max'


def main():
    # Read parameters from CLI
    state = parse_args(sys.argv)
    (queryParameter, _, _, _) = state

    t = Node.getFromInputState(state)

    print('Tree:   ', queryParameter)
    print('Height: ', t.height)

    total_per_levels = 0
    for i in range(0, t.height):
        total_i = t.countInLevel(i)
        total_per_levels += total_i
        print('Total in level:', i, total_i)

    print(total_per_levels)


if __name__ == "__main__":
    main()
