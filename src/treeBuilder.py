import sys
from Node import Node
from util import list_subcategories, parse_args


def main():
    # Read parameters from CLI
    state = parse_args(sys.argv)
    (queryParameter, _, _, _) = state

    t = Node.getFromInputState(state)

    print('Tree built!')
    print('Saved to:', Node.getFilePath(state))


if __name__ == "__main__":
    main()
