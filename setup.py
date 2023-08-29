from setuptools import setup, find_packages

setup(
    name='HotSinglesInYourArea',
    version='0.0.0',
    py_modules=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'hotsinglessinyourarea = src.cli:cli',
        ],
    },
)
