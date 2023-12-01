from setuptools import setup

with open("app/README.md", "r") as f:
    long_description = f.read()

setup(
    name="anycache",
    version="0.1.0",
    description=(
        "Anycache: A Python library for disk-based caching of function results, supporting sync/async functions and "
        "generators"
    ),
    packages=["anycache"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/borisrakovan/anycache",
    author="Boris Rakovan",
    author_email="b.rakovan@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Programming Language :: Python :: 3.10",
        'Programming Language :: Python :: 3.11',
        "Operating System :: OS Independent",
        "Framework :: AsyncIO",
        "Typing :: Typed",
    ],
    install_requires=["bson >= 0.5.10"],
    extras_require={
        "dev": ["pytest>=7.0", "twine>=4.0.2"],
    },
    python_requires=">=3.10",
)
