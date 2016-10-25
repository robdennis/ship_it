import click
from ship_it import fpm

@click.command()
@click.option('--requirements', default=None, help='Path to requirements.txt')
@click.option('--setup', default=None, help='Path to setup.py')
@click.argument('manifest')
def main(manifest, requirements, setup):
    fpm(manifest, requirements, setup)

if __name__ == '__main__':
    main()
