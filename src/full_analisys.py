import os, sys
from util import parse_args

def main():
	try:
		state = parse_args(sys.argv)
	except Exception:
		raise
		exit()

	args = '"' + str(state[0]) + '" "' + str(state[1]) + '" ' + str(state[2]) + ' ' + str(state[3])

	print('Building tree...')
	os.system('python3 treeBuilder.py ' + args)

	print('\n==================\n')

	print('Extracting tree metrics...')
	os.system('python3 treeMetrics.py ' + args)

	print('\n==================\n')

	print('Extracting important terms from tree...')
	os.system('python3 termsExtractor.py ' + args)

	print('\n==================\n')
	print('Identifying specialists...')
	os.system('python3 identifySpecialists.py ' + args)

if __name__ == "__main__":
	main()