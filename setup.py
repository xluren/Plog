from setuptools import setup, find_packages
setup(
    name='Plog',
    version='0.1',
    description='Plog -- a parse-log tool ',
    author='xluren',
    author_email='xlurenn@gmail.com',
    license = "MIT",
    packages= find_packages(),
    url='https://github.com/xluren',
    scripts = ["plog.py"],
)
