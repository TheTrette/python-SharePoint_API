import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SharePoint_API",
    version="2022.03.02",
    author="Matthew Trette",
    author_email="matt.trette@me.com",
    description="python wrappers for SharePoint REST API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TheTrette/python-SharePoint_API",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)


# python3 setup.py sdist