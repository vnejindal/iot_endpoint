# !/bin/bash

####################################################################
# This script will be used for upgrade and downgrade iot83 releases
# 
####################################################################

set +x
pushd () {
    command pushd "$@" > /dev/null
}

popd () {
    command popd "$@" > /dev/null
}

usage()
{
    echo "Usage: $0 [params] status|<install release.tar.gz>|cutover|revert|start"
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
#if [ ! -f $CONFIG_FILE ];then 
#    echo "Installation corrupt"
#    exit 1
#fi 
ACTIVE_REL=`cat $REL_DIR/$CONFIG_FILE | grep active | cut -f2 -d':'`
BACKUP_REL=`cat $REL_DIR/$CONFIG_FILE| grep backup | cut -f2 -d':'`

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
   echo "Active  $ACTIVE_REL" 
   echo "Backup  $BACKUP_REL" 
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

install_package()
{
    cd $mod_name
    echo "-----------------------------------------"
    echo "Installing $mod_name package"
    ./install.sh install
    echo "$mod_name package installed successfully."
    echo "-----------------------------------------"
    cd -
}
## Will unarchive each of individual modules and 
# install them 
#
install_modules()
{

    set +x
    cd $REL_DIR/$RELS_DIR/$RELEASE_NAME 
    for modinfo in `cat modules`
    do 
        mod_name=`echo $modinfo | cut -f1 -d':'`
        mod_rel=`echo $modinfo | cut -f2 -d':'`
        mod_file=${mod_name}_${mod_rel}.tar.gz
        sha_file=${mod_name}_${mod_rel}.sha
        if [ ! -f $mod_file ]; then 
             echo "Module: $module_file does not exist"
             exit 1
        fi 
        sha512sum -c $sha_file
        if [ $? -eq 0 ]; then 
             echo "sha match successful"
             tar -zxvf $mod_file
             install_package
        else
             echo "invalid module: sha does not match"
             exit 1
        fi
    done
}

## Start each modules listed in modules
start_modules()
{
    set +x
    cd $REL_DIR/$CUR_DIR
    for modinfo in `cat modules`
    do
        mod_name=`echo $modinfo | cut -f1 -d':'`
        mod_rel=`echo $modinfo | cut -f2 -d':'`


        cd $mod_name
        echo "-----------------------------------------"
        echo "Starting $mod_name module"
        echo "-----------------------------------------"
        ./install.sh start
        echo "$mod_name package started successfully."
        echo "-----------------------------------------"
        cd -
    done
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
    ACTIVE_REL=$RELEASE_NAME
    BACKUP_REL=$RELEASE_NAME
    echo "active:$RELEASE_NAME" > $CONFIG_FILE
    echo "backup:$RELEASE_NAME" >> $CONFIG_FILE
  else
    if [ $ACTIVE_REL != $BACKUP_REL ]; then
       mv $RELS_DIR/$BACKUP_REL $ARCHIVE_DIR
    fi
    BACKUP_REL=$RELEASE_NAME
    echo "active:$ACTIVE_REL " > $CONFIG_FILE
    echo "backup:$RELEASE_NAME" >> $CONFIG_FILE
  fi 
  cp $RELEASE_FILE $ARCHIVE_DIR
  \rm -rf $TMP_DIR
  install_modules 
}

cutover_release()
{
   set +x
   cd $REL_DIR
   if [ ! -f $CONFIG_FILE ];then 
       echo "Installation corrupt"
       exit 1
   fi 

   rm $CUR_DIR
   ln -fs $RELS_DIR/$BACKUP_REL $CUR_DIR
   echo "active:$BACKUP_REL" > $CONFIG_FILE
   echo "backup:$ACTIVE_REL" >> $CONFIG_FILE
   echo "cutover complete"
}

COMMAND=$1
#echo "Command is $COMMAND"

pushd $PWD
case $COMMAND in 
status)
show_status
;;
install)
RELEASE_FILE=$2
install_release
;;
start)
start_modules
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
