#!/bin/bash

# Run tests from the root directory
cd tests
python -m pytest "$@" 