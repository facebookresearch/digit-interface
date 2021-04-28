# Copyright (c) Facebook, Inc. and its affiliates. All rights reserved.
import os

import nox

BASE = os.path.abspath(os.path.dirname(__file__))

DEFAULT_PYTHON_VERSIONS = ["3.7"]

LINT_SETUP_DEPS = ["black", "flake8", "flake8-copyright", "isort"]
DEPLOY_SETUP_DEPS = ["twine"]

VERBOSE = os.environ.get("VERBOSE", "0")
SILENT = VERBOSE == "0"

USING_CI = os.environ.get("USING_CI", False)
PYPI_USERNAME = os.environ.get("PYPI_USERNAME", None)
PYPI_PASSWORD = os.environ.get("PYPI_PASSWORD", None)


def _base_install(session):
    session.install("--upgrade", "setuptools", "pip", silent=SILENT)


def install_lint_deps(session):
    _base_install(session)
    session.install(*LINT_SETUP_DEPS, silent=SILENT)


def install_deploy_deps(session):
    _base_install(session)
    session.install(*DEPLOY_SETUP_DEPS, silent=SILENT)


def install_pytouch(session):
    session.chdir(BASE)
    session.run("pip", "install", "-e", ".")


@nox.session(python=DEFAULT_PYTHON_VERSIONS)
def lint(session):
    install_lint_deps(session)
    session.run("black", "--diff", "--check", ".", silent=SILENT)
    session.run(
        "isort",
        "--check",
        "--diff",
        ".",
        "--skip=.nox",
        silent=SILENT,
    )
    session.run("flake8", "--config", ".flake8")


@nox.session(python=DEFAULT_PYTHON_VERSIONS)
def tests(session):
    _base_install(session)
    install_pytouch(session)
    session.install("pytest")
    session.run("pytest", "tests")


@nox.session(python=DEFAULT_PYTHON_VERSIONS)
def build(session):
    _base_install(session)
    session.run("rm", "-rf", "dist", external=True)
    session.run("python", "setup.py", "sdist")


@nox.session(python=DEFAULT_PYTHON_VERSIONS)
def deploy(session):
    if not USING_CI:
        session.skip("Skipping deployment to PyPi.")
    install_deploy_deps(session)
    session.run(
        "twine",
        "upload",
        "dist/*",
        env={"TWINE_USERNAME": PYPI_USERNAME, "TWINE_PASSWORD": PYPI_PASSWORD},
    )
