from setuptools import find_packages
from setuptools import setup

version = "0.0.1"

setup(
    name="passerelle-imio-keycloak",
    version=version,
    author="iMio",
    author_email="support-ts@imio.be",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Environment :: Web Environment",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
    ],
    url="https://github.com/IMIO/passerelle-imio-keycloak",
    install_requires=[
        "django>=3.2, <3.3",
    ],
    zip_safe=False,
)
