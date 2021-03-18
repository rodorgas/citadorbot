import sys
import textwrap


def wrap(text):
    result = textwrap.wrap(text, width=10, replace_whitespace=False)
    print('\n'.join(result))

if __name__ == '__main__':
    wrap(sys.argv[1])
