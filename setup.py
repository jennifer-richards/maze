from setuptools import setup, find_packages

setup(
    name='Maze',
    version='0.1',
    description='Maze generator and interactive game',
    author='Jennifer Richards',
    author_email='jeni@borkbork.org',
    url='',
    license='',
    install_requires=[
        'matplotlib',
        'PaperSize',
        'tqdm'
    ],
    packages=find_packages(
        exclude=['venv']
    ),
    entry_points={
        'console_scripts': ['mazegen=maze.gen:main']
    },
    include_package_data=True
)
