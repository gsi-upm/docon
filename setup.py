from setuptools import setup
from pip.req import parse_requirements

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements("requirements.txt")

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in install_reqs]

VERSION = "0.1.1"

print(reqs)

setup(
    name='docon',
    packages=['docon'],  # this must be the same as the name above
    version=VERSION,
    description="""
    A sentiment analysis server implementation. Designed to be \
extendable, so new algorithms and sources can be used.
    """,
    author='J. Fernando Sanchez',
    author_email='balkian@gmail.com',
    url='https://github.com/gsi-upm/docon',  # use the URL to the github repo
    download_url='https://github.com/gsi-upm/docon/archive/{}.tar.gz'
    .format(VERSION),
    keywords=['conversion', 'templates', 'flask', 'celery', 'eurosentiment', 'nif', 'gsi'],
    classifiers=[],
    install_requires=reqs,
    include_package_data=True,
    entry_points="""
        [console_scripts]
        docon=docon.cli:run_cli
    """
)
