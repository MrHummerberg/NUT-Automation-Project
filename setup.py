from setuptools import setup, find_packages

setup(
    name="nut_automation",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "nut-setup=nut_automation.main:main",
        ],
    },
    install_requires=[
        # Add dependencies here if any, e.g., 'requests'
    ],
    author="MrHummerberg",
    description="Automation script for NUT virtual UPS configuration",
    python_requires=">=3.7",
)
