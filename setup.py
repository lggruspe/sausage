from pathlib import Path
import setuptools

setuptools.setup(
    name="ssg",
    version="0.0.0",
    author="Levi Gruspe",
    author_email="mail.levig@gmail.com",
    description="Create static sites using Jinja2 templates",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/lggruspe/ssg",
    packages=setuptools.find_packages(),
    classifiers=[
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    install_requires=["Jinja2>=3.0.1"],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "ssg=ssg.__main__:main"
        ]
    }
)
