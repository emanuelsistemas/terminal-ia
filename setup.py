from setuptools import setup, find_packages

setup(
    name="chat-ia",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "groq>=0.4.2",
        "openai>=1.12.0",
        "python-dotenv>=1.0.1",
    ],
    entry_points={
        "console_scripts": [
            "chat-ia=src.main:main",
        ],
    },
)
