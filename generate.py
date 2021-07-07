import argparse
import yaml
import os

from jinja2 import Environment, FileSystemLoader

parser = argparse.ArgumentParser(description="generate my personal site.")
parser.add_argument("cv", type=str, help='A Yaml file representing the CV.')
parser.add_argument('template', type=str,
                    help='template file to generate Html from.')
parser.add_argument('-o', '--output', type=str,
                    help='final output file. stdout if not specified')


def main():
    result = parser.parse_args()
    with open(result.cv) as fd:
        cv = yaml.load(fd)

    env = Environment(loader=FileSystemLoader(os.path.abspath(os.path.join(
        result.template, os.path.pardir))), trim_blocks=True, lstrip_blocks=True)
    tmpl = env.get_template(os.path.basename(result.template))

    if result.output is None:
        print(tmpl.render(**cv))
    else:
        with open(result.output, 'w') as fd:
            fd.write(tmpl.render(**cv))


if __name__ == '__main__':
    main()
