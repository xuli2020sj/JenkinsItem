#!/bin/bash

echo dir $1
echo source $2
echo config $3
echo build type: $4

cd $1 || exit 1
source $2 || exit 1
config $3 || exit 1
build $4 || exit 1
clean $4 || exit 1