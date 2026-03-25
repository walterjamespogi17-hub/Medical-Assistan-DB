from setuptools import setup, find_packages

setup(
    name="medical-assistant-robot",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        # Add dependencies from requirements.txt
    ],
    entry_points={
        'console_scripts': [
            'medical-robot = app.app:app',
        ],
    },
)