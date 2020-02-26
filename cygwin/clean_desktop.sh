#!/bin/bash
# Simple (cygwin) bash script to remove all 
# files (no links) from your Windows Desktop

# Change DEFAULTDIR or use parameter from command line
DEFAULTDIR="$HOME/Desktop"
DIR=${1:-$DEFAULTDIR}
cd $DIR || exit

SOURCE=$(pwd)

SOURCE=${SOURCE#/cygdrive/}

# Change TARGET for your needs
TARGET="c:\Archive\\"$SOURCE

echo "SOURCE is $SOURCE."
echo "TARGET is $TARGET."

ls

GLOBIGNORE=*.lnk:*.ini:*.url

mkdir -p "$TARGET" || exit

mv -v *.* "$TARGET" || exit

unset GLOBIGNORE
