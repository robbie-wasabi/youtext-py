from setuptools import setup, find_packages

setup(
    name="youtext",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "youtube_transcript_api",
        "openai",
    ],
    entry_points={
        "console_scripts": [
            "youtext=script:main",
        ],
    },
)