#!/bin/bash
set -e
cd $(dirname $0)

if [[ -e venv ]]; then
    source venv/bin/activate
fi

git pull
make
