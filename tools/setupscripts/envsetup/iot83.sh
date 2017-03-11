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
## Configuration Files 
CONFIG_DIR=$BASE_DIR/config
## Release directory 
REL_DIR=$BASE_DIR/release
## Environment Config 
ENV_CONFIG=$BASE_DIR/envsetup/.config
LOG_FILE=${PWD##*/}.log
COMMAND_OPTS="$@"
DRYRUN=0

RELEASE_FILE=''
RELEASE_NAME=''
RELS_DIR=releases
CUR_DIR=current
ARCHIVE_DIR=.archive
CONFIG_FILE=.config

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


show_status()
{
   cd $REL_DIR
   if [ ! -f $CONFIG_FILE ];then 
       echo "Installation corrupt"
       exit 1
   fi 

   act_rel=`cat $CONFIG_FILE | grep active | cut -f2 -d':'`
   bk_rel=`cat $CONFIG_FILE | grep backup | cut -f2 -d':'`
   echo "Active  $act_rel" 
   echo "Backup  $bk_rel" 
}

validate_setup()
{
   retval=0
   if [ ! -d $RELS_DIR ]; then 
      echo "setup incomplete"
   elif [ ! -d $ARCHIVE_DIR ]; then 
      echo "setup incomplete"
   elif [ ! -f $RELEASE_FILE ]; then
      echo "$RELEASE_FILE not present"
   else
      retval=1
   fi
   if [ $retval = "0" ]; then
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
  set +x
  cd $REL_DIR
  validate_setup
  
  if [ -d $TMP_DIR ]; then 
     \rm -rf $TMP_DIR
  fi 
  mkdir -v $TMP_DIR
  cp $RELEASE_FILE $TMP_DIR
  pushd $PWD
  cd $TMP_DIR
  tar -zxvf $RELEASE_FILE
  RELEASE_NAME=`ls | grep -v tar`
  #vne::tbd:: check return value of tar command
  popd 
  #
  mv $TMP_DIR/$RELEASE_NAME $RELS_DIR
  if [ ! -f $CONFIG_FILE ]; then 
    echo "Initial installation"
    ln -fs $RELS_DIR/$RELEASE_NAME $CUR_DIR
    echo "active:$RELEASE_NAME" > $CONFIG_FILE
    echo "backup:$RELEASE_NAME" >> $CONFIG_FILE
  else
    act_rel=`cat $CONFIG_FILE | grep active | cut -f2 -d':'`
    bk_rel=`cat $CONFIG_FILE| grep backup | cut -f2 -d':'`
    if [ $act_rel != $bk_rel ]; then
       mv $RELS_DIR/$bk_rel $ARCHIVE_DIR
    fi
    echo "active:$act_rel" > $CONFIG_FILE
    echo "backup:$RELEASE_NAME" >> $CONFIG_FILE
  fi 
  cp $RELEASE_FILE $ARCHIVE_DIR
  \rm -rf $TMP_DIR
}

cutover_release()
{
   set +x
   cd $REL_DIR
   if [ ! -f $CONFIG_FILE ];then 
       echo "Installation corrupt"
       exit 1
   fi 

   act_rel=`cat $CONFIG_FILE | grep active | cut -f2 -d':'`
   bk_rel=`cat $CONFIG_FILE | grep backup | cut -f2 -d':'`
   rm $CUR_DIR
   ln -fs $RELS_DIR/$bk_rel $CUR_DIR
   echo "active:$bk_rel" > $CONFIG_FILE
   echo "backup:$act_rel" >> $CONFIG_FILE
   echo "cutover complete"
}

COMMAND=$1
echo "Command is $COMMAND"


pushd $PWD
case $COMMAND in 
status)
show_status
;;
install)
RELEASE_FILE=$2
install_release
;;
cutover)
cutover_release
;;
revert)
cutover_release
;;
*)
echo Unsupported Option: "$COMMAND"
usage
;;
esac
popd 
