import setuptools

with open("../README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sysmon",
    version="1.0.0",
    author="Matthias Schinzel",
    author_email="unused@unused.com",
    description="System Monitor for Linux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MatthiasSchinzel/sysmon",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ['sysmon=sysmon.sysmon:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.6',
    install_requires=[
        "pyqtgraph",
        "pyqt5>=5",
        "numpy>=1"
    ],
    package_data={'sysmon': ['*.ui']},
    include_package_data=True,
)
