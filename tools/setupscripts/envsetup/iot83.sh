# !/bin/bash

####################################################################
# This script will be used for upgrade and downgrade iot83 releases
# 
####################################################################

set +x
usage()
{
    echo "Usage: $0 [params] status|<install release.tar.gz>|cutover|revert"
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
INSTALL_DIR=/tmp
BASE_DIR=$INSTALL_DIR/iot
CONFIG_DIR=$BASE_DIR/config
REL_DIR=$BASE_DIR/release
LOG_FILE=${PWD##*/}.log
CONFIG_FILE=install.config
COMMAND_OPTS="$@"
DRYRUN=0

RELEASE_FILE=''
CUR_DIR=current
RELS_DIR=releases
ARCHIVE_DIR=.archive
CONFIG_FILE=.config

{

} >> $LOG_FILE 2>&1

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

##vne::tbd:: read INSTALL_DIR
show_status()
{

   

}

validate_setup()
{
   retval=0
   if [ ! -d $RELS_DIR ]; then 
      echo "setup incomplete"
   elif [ ! -d $ARCHIVE_DIR ]; then 
      echo "setup incomplete"
   elif [ ! -f $CONFIG_FILE ]; then 
      echo "setup incomplete"
   elif [ ! -f $RELEASE_FILE ]; then
   else
   retval=1
   fi
   if [ $retval = "1" ]; then
      exit 1
   fi
}
install_release()
{
  #check if primary, secondary and active directories exists
  #create a tmp directory and unzip the release in it
  #
  # mv secondary to archive

  #if any failure occurs, rollback to earlier version
  TMP_DIR=tmp
  set -x
  cd $REL_DIR
  validate_setup
  
  if [ -d $TMP_DIR ]; then 
     rm -rf $TMP_DIR
  fi 
  mkdir -v $TMP_DIR
  cp $RELEASE_FILE $TMP_DIR
  pushd $PWD
  cd $TMP_DIR
  tar -zxvf $RELEASE_FILE
  #vne::tbd:: check return value of tar command
  popd 
  #copy this release dir to releases directory 
  #take a backup of .config file 
  #read .config file and get active and backup release
  #update .config file to mark backup as new directory 
  #
  if [! -d $CUR_DIR ]; then 
    echo "First installation"
    #update .config file to mark current release as new 
    # mark current release to synlink to new 
  fi 
  #mv backup release to .archive dir 
}

restore_backup()
{
}
COMMAND=$1
echo "Command is $COMMAND"


case $COMMAND in 
status)
show_status
;;
install)
pushd $PWD
RELEASE_FILE=$2
install_release
popd 
;;
cutover)
cutover_release
;;
revert)
revert_release
;;
*)
echo Unsupported Option: "$COMMAND"
usage
;;
esac
