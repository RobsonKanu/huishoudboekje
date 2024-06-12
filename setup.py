""""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

setup(
    long_description=readme,
    include_package_data=True,
    keywords='project_huishoudboekje',
    name='project_huishoudboekje',
    install_requires=open('requirements.txt').read().splitlines(),
    package_dir={"": 'src'},
    packages=find_packages(include=['src']),
    zip_safe=False
)