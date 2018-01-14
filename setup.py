from setuptools import setup, find_packages

setup(
    name='Maze',
    version='0.1',
    packages=find_packages(
        exclude=['venv']
    ),
    url='',
    license='',
    author='Jennifer Richards',
    author_email='jeni@borkbork.org',
    description='Maze generator and interactive game',
    entry_points={
        'console_scripts': ['mazegen=maze.gen.main']
    }
)
