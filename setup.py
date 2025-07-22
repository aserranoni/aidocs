from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aidocs",
    version="0.1.0",
    author="Ariel Serranoni",
    author_email="ariel@example.com",
    description="A CLI tool for managing AI assistant context documentation across development projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arielserranoni/aidocs",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: Markup",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    keywords="ai documentation cli symlinks context",
    entry_points={
        'console_scripts': [
            'aidocs = aidocs_pkg.main:main',
        ],
    },
    install_requires=[
        # No external dependencies - uses only Python stdlib
    ],
    project_urls={
        "Bug Tracker": "https://github.com/arielserranoni/aidocs/issues",
        "Source": "https://github.com/arielserranoni/aidocs",
    },
)
