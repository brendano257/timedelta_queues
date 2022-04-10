from setuptools import setup

setup(
    name='timedelta_queues',
    url='https://github.com/brendano257/timedelta_queues',
    author='Brendan Blanchard',
    author_email='brendano257@gmail.com',
    packages=['timedelta_queues'],
    install_requires=['numpy'],
    version='0.1',
    license='MIT',
    description='Queues that evict items based on timedeltas from head to tail, rather than a maximum length in items.',
    long_description=open('README.md').read(),
)
