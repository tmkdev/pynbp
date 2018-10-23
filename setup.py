import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pynbp",
    version=pynbp.__version__,
    author="Terry Kolody",
    author_email="tekolody@gmail.com",
    description="Python implementation og the HP Tuners Track Addict Numeric Broadcast Protocol (V1.0)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tmkdev/pynbp",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
    install_requires=[
       'pyserial',
    ]
)