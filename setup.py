from setuptools import setup, find_packages


install_requires = ["miniconfig>=0.5.2", "metashape>=0.0.2", "prestring>=0.9.0"]
tests_requires = ["pytest", "pytest-cov"]
extras_require = {
    "testing": tests_requires,
    "dev": tests_requires + ["black", "flake8", "mypy"],
}
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
    extras_require=extras_require,
    tests_require=tests_requires,
    test_suite="egoist.tests",
    package_data={"egoist": ["py.typed"]},
    entry_points="""
      [console_scripts]
      egoist = egoist.cli:main
""",
)
