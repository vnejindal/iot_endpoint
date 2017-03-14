### This script creates a software release###
# !/bin/bash

set +x
usage()
{
    echo "Usage: $0 [params] create <release directory>|<check <release sha>"
    echo "params can be one of following:"
    echo "    --help | -h        : Print out this help message"
    echo "    --dry-run| -d      : Dry run the utility without actually changing anything"
    exit 1
}

if test $# -lt 1; then
	usage
fi
COMMAND=$1
SW_DIR=$2
PKG_DIR=packages
MAVER=''
MIVER=''
BUVER=''

echo "Command is $COMMAND"

get_version()
{
REL_FILE="$SW_DIR/release"
MAJOR='major'
MINOR='minor'
BUILD='build'
DELIM=":"
MAVER=`cat $REL_FILE | grep $MAJOR | cut -f2 -d"$DELIM"`
MIVER=`cat $REL_FILE | grep $MINOR | cut -f2 -d"$DELIM"`
BUVER=`cat $REL_FILE | grep $BUILD | cut -f2 -d"$DELIM"`
echo "version - $MAVER.$MIVER.$BUVER"
echo "version: $MAVER.$MIVER.$BUVER; Build Date - `date`" >> $REL_FILE
}

create_release()
{
  set -x
  if [ ! -d $SW_DIR ]; then
     echo "$SW_DIR does not exist"
     return 1
  fi

  get_version
  RELEASE_NAME=${SW_DIR}_$MAVER.$MIVER.$BUVER
  if [ -d $RELEASE_NAME ]; then 
     \rm -rf $RELEASE_NAME
  fi
  mkdir -v $RELEASE_NAME
  cp $SW_DIR/* $RELEASE_NAME
  #copy respective modules in release directory
  for module in `cat $SW_DIR/modules`
  do 
      mname=`echo $module | cut -f1 -d':'`
      mrel=`echo $module | cut -f2 -d':'`
      pname="${mname}_${mrel}.tar.gz"
      psha="${mname}_${mrel}.sha"
      if [ ! -f $PKG_DIR/$pname ] || [ ! -f $PKG_DIR/$psha ] ; then 
         echo "Package $pname does not exist"
         exit 1
      fi
      cp $PKG_DIR/$pname $RELEASE_NAME
      cp $PKG_DIR/$psha $RELEASE_NAME
  done

  tar -cvf ${RELEASE_NAME}.tar $RELEASE_NAME
  gzip ${RELEASE_NAME}.tar
  echo "Software Release: ${RELEASE_NAME}.tar.gz"
  sha512sum ${RELEASE_NAME}.tar.gz > ${RELEASE_NAME}.sha
  rm -rf $RELEASE_NAME
}

check_release()
{
sha512sum -c $SW_DIR
}
case $COMMAND in 
create)
create_release
;;
check)
check_release
;;
*)
echo Unsupported Option: "$COMMAND"
usage
;;
esac
