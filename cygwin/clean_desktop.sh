#!/bin/bash
# Simple (cygwin) bash script to remove all 
# files (no links) from your Windows Desktop

# Change DEFAULTDIR or use parameter from command line
DEFAULTDIR="/cygdrive/c/$HOMEPATH/Desktop"
DIR=${1:-$DEFAULTDIR}
cd $DIR

SOURCE=$(pwd)

SOURCE=${SOURCE#/cygdrive/}

# Change TARGET for your needs
TARGET="e:\Archive\\"$SOURCE

echo "SOURCE is $SOURCE."
echo "TARGET is $TARGET."

ls

GLOBIGNORE=*.lnk:*.ini:*.url

mkdir -p "$TARGET"

mv -v *.* "$TARGET"

unset GLOBIGNORE