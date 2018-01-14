from setuptools import setup

setup(
    name='Maze',
    version='0.1',
    packages=[
        'maze',
        'maze.resources'
    ],
    url='',
    license='',
    author='Jennifer Richards',
    author_email='jeni@borkbork.org',
    description='Maze generator and interactive game',
    entry_points={
        'console_scripts': ['mazegen=maze.gen.main']
    }
)
