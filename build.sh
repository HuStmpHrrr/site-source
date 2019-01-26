#!/bin/bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
OUTPUT_DIR=
INPUT_DIR=.

while getopts i:o: OPT; do
    case $OPT in
        i) INPUT_DIR=$OPTARG;;
        o) OUTPUT_DIR=$OPTARG;;
        :)
            echo "-$OPTARG needs an argument" >&2
            exit 1;;
        \?)
            echo "unknown option -"$OPTARG >&2
            exit 1;;
    esac
done

if [[ $OUTPUT_DIR == "" ]]; then
    echo "need an output folder! -o something" >&2
    exit 1
fi

if [[ ! -d $INPUT_DIR ]]; then
    echo "input folder $INPUT_DIR is not a folder! " >&2
    exit 1
fi

mkdir -p "$OUTPUT_DIR"
cp -r "$INPUT_DIR/static/"* "$OUTPUT_DIR/"
python "$DIR/generate.py" "$DIR/CV.yaml" "$DIR/index.tmpl" -o "$OUTPUT_DIR/index.html"
mkdir -p "$OUTPUT_DIR/zh"
python "$DIR/generate.py" "$DIR/CV.zh.yaml" "$DIR/index.zh.tmpl" -o "$OUTPUT_DIR/zh/index.html"
