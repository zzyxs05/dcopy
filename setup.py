from setuptools import setup, find_packages

setup(
    name="dcopy",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "dcopy = dcopy.main:run"
        ]
    },
    install_requires=[
        "pyperclip>=1.8.2",
    ],
    url="https://github.com/zzyxs05/dcopy",
)
