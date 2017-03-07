### This script creates a software package ###
# !/bin/bash

set +x
usage()
{
    echo "Usage: $0 [params] <create <directory name> | check <package sha>"
    echo "params can be one of following:"
    echo "    --help | -h        : Print out this help message"
    echo "    --dry-run| -d      : Dry run the utility without actually changing anything"
    exit 1
}

if test $# -lt 1; then
	usage
fi
COMMAND=$1
PKG_DIR=$2
MAVER=''
MIVER=''
BUVER=''
echo "Command is $COMMAND"

get_version()
{
REL_FILE='release'
MAJOR='major'
MINOR='minor'
BUILD='build'
DELIM=":"
MAVER=`cat $REL_FILE | grep $MAJOR | cut -f2 -d"$DELIM"`
MIVER=`cat $REL_FILE | grep $MINOR | cut -f2 -d"$DELIM"`
BUVER=`cat $REL_FILE | grep $BUILD | cut -f2 -d"$DELIM"`
echo "version - $MAVER.$MIVER.$BUVER"
}

create_pkg()
{
  set -x
  if [ ! -d $PKG_DIR]; then
     echo "$PKG_DIR does not exist"
     return 1
  fi
  cd $PKG_DIR; get_version; cd -
  PACKAGE_NAME=${PKG_DIR}_$MAVER.$MIVER.$BUVER
  tar -cvf ${PACKAGE_NAME}.tar $PKG_DIR
  gzip ${PACKAGE_NAME}.tar
  echo "Software Package: ${PACKAGE_NAME}.tar.gz"
  sha512sum ${PACKAGE_NAME}.tar.gz > ${PACKAGE_NAME}.sha
}

check_pkg()
{
sha512sum -c $PKG_DIR
}
case $COMMAND in 
create)
create_pkg
;;
check)
check_pkg
;;
*)
echo Unsupported Option: "$COMMAND"
usage
;;
esac
