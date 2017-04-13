# !/bin/bash

################################################################
# This script will setup the environment on hardware. 
# It is needed only the first time 
# Release Structure
# install_dir/iot83/release/
#    |- .archive (d) 
#    |- .config (f)
#          |- active:
#          |- backup:
#    |- releases (d)
#################################################################

set +x
usage()
{
    echo "Usage: $0 [params] setup|remove"
    #echo "params can be one of following:"
    #echo "    --version | -v     : Print out Software version and exit"
    echo "    --help | -h        : Print out this help message"
    #echo "    --dry-run| -d      : Dry run the utility without actually changing anything"
    exit 1
}

if test $# -lt 1; then
	usage
fi

#### GLOBAL VARIABLES ####
INSTALL_DIR=/opt
BASE_DIR=$INSTALL_DIR/iot83
CONFIG_DIR=$BASE_DIR/config
REL_DIR=$BASE_DIR/release
ENV_DIR=$BASE_DIR/envsetup

#CUR_DIR=current
RELS_DIR=releases
ARCHIVE_DIR=.archive

LOG_FILE=${PWD##*/}.log
COMMAND_OPTS="$@"
DRYRUN=0

#{
#
#} >> $LOG_FILE 2>&1

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

while true
do
    case "$1" in
    --version | -v)
        get_version
	exit 0
	;;
    -h | --help)
	usage
	;;
    -d | --dry-run)
	DRYRUN=1
        shift
	;;
    -*)
	echo Unsupported Option: "$1"
	usage
	;;
    *)
	break
	;;
    esac
done


setup()
{

  set -x
  echo "Setting up the enviornment..."
  if [ ! -d $INSTALL_DIR ]; then
     echo "$INSTALL_DIR does not exist. Creating it..."
     mkdir $INSTALL_DIR
  fi 

  pushd $PWD
  cd $INSTALL_DIR
  (mkdir -v $BASE_DIR)
  (mkdir -v $CONFIG_DIR $REL_DIR $ENV_DIR)
  cd $REL_DIR
  mkdir -v $RELS_DIR $ARCHIVE_DIR
  #ln -s $PRIM_DIR $CUR_DIR
  popd
  cp -rf * $ENV_DIR
  echo "install_path:$INSTALL_DIR" > $ENV_DIR/.config
  echo "date:`date`" >> $ENV_DIR/.config
  mv $ENV_DIR/env.config $CONFIG_DIR
}
remove()
{
    echo "cleaning up the environment"
    ./iot83.sh stop
    \rm -rf $BASE_DIR
}
COMMAND=$1
echo "Command is $COMMAND"


case $COMMAND in 
setup)
setup
;;
remove)
remove
;;
*)
echo Unsupported Option: "$COMMAND"
usage
;;
esac
