#!/bin/bash

# Validation is not added but an argument is
# mandatory for running this script

docker build -t fonapi_image:$1 .
