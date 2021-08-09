from pathlib import Path
import setuptools

setuptools.setup(
    name="sausage",
    version="0.0.0",
    author="Levi Gruspe",
    author_email="mail.levig@gmail.com",
    description="A flexible template-based static site generator",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/lggruspe/sausage",
    packages=setuptools.find_packages(),
    package_data={
        "sausage": ["data/*", "data/**/*"]
    },
    classifiers=[
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    install_requires=[
        "Jinja2>=3.0.1",
        "PyYAML>=5.4.1",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "ssg=sausage.__main__:main"
        ]
    }
)
