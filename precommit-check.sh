#!/usr/bin/env bash

# bash
set -Eeuo pipefail

# zsh
#set -e PIPE_FAIL
#set -x


swift package clean
swift build -Xswiftc -warnings-as-errors

latexmk -C
latexmk -time -pdf -interaction=nonstopmode -Werror -logfilewarninglist main

INPUTFILES=`cat main.fls | grep INPUT | grep -v "/usr/local" | sort | uniq | cut -f 2 -d ' ' `

# zsh does only find one word in $INPUTFILES
for file in $INPUTFILES
do
  git status -s $file
done
