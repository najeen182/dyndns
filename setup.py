from setuptools import setup, find_packages
import versioneer


setup(
    name="jfddns",
    author="Josef Friedrich",
    author_email="josef@friedrich.rocks",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Simple dynamic ddns update tool using HTTP",
    url="https://github.com/Josef-Friedrich/jfddns",
    packages=find_packages(),
    install_requires=[
        'dnspython',
        'flask',
        'PyYAML',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points = {
        'console_scripts': [
            'jfddns-debug = jfddns:debug',
        ],
    },
)
