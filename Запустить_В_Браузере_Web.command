#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR/ClothesHelper_App"
python3 "$DIR/ClothesHelper_App/web_app.py"
