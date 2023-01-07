import setuptools
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

with open("README.md", "r") as fh:
    long_desc = fh.read()


def read_requirements():
    reqs_path = os.path.join(__location__, 'requirements.txt')
    with open(reqs_path, encoding="utf8") as f:
        reqs = [line.strip() for line in f if not line.strip().startswith('#')]

    names = []
    for req in reqs:
        names.append(req)
    return {'install_requires': names}


setuptools.setup(
    name="gerbil-api-wrapper",
    version="1.0.1",
    author="Paul Heinze",
    author_email="paul.heinze@student.hs-anhalt.de",
    description="A package that provides wrapper functionality for the Gerbil Benchmark Service",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/heinpa/GerbilExperimentApiWrapper",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    **read_requirements()
)

