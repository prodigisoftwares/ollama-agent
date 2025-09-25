#!/bin/bash

clear;

# Run specific pre-commit hooks
pre-commit run isort --all-files --verbose
pre-commit run flake8 --all-files --verbose
pre-commit run tests --all-files --verbose
pre-commit run coverage --all-files --verbose
