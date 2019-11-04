import sys
import textwrap


def wrap(text):
    result = textwrap.wrap(text, width=30)
    print('\n'.join(result))

if __name__ == '__main__':
    wrap(sys.argv[1])
