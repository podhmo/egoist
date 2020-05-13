from setuptools import setup, find_packages


install_requires = ["miniconfig>=0.5.1", "metashape>=0.0.1", "prestring>=0.9.0"]
dev_requires = ["black", "flake8", "mypy"]
tests_requires = ["pytest", "pytest-cov"]

setup(
    classifiers=[
        # "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
    ],
    python_requires=">=3.7",
    packages=find_packages(exclude=["egoist.tests"]),
    install_requires=install_requires,
    extras_require={"testing": tests_requires, "dev": dev_requires},
    tests_require=tests_requires,
    test_suite="egoist.tests",
    package_data={"egoist": ["py.typed"]},
    entry_points="""
      [console_scripts]
      egoist = egoist.cli:main
""",
)
