# !/bin/bash

set +x
usage()
{
    echo "Usage: $0 [params] install|uninstall|start|stop"
    echo "params can be one of following:"
    echo "    --version | -v     : Print out Software version and exit"
    echo "    --help | -h        : Print out this help message"
    echo "    --dry-run| -d      : Dry run the utility without actually changing anything"
    exit 1
}

if test $# -lt 1; then
	usage
fi

#### GLOBAL VARIABLES ####
LOG_FILE=${PWD##*/}.log
CONFIG_FILE=install.config
COMMAND_OPTS="$@"
DRYRUN=0

{
env_validate()
{
DELIM=":"
if [ ! -f $CONFIG_FILE ]; then
  echo ' $CONFIG_FILE does not exist. Incomplete installation. Exiting'
  exit 1
fi 
OS=`cat $CONFIG_FILE | grep 'os' | cut -f2 -d"$DELIM"`
os_ver=`uname -a | awk {'print $2'}`
if [ $os_ver != $OS ] ; then
  echo 'OS version: $os_ver not supported. Exiting.'
  exit 1
fi 

##vne::tbd::
#if [ `whoami` != 'root' ]; then 
#  echo 'User is not root. Exiting'
#  exit 1
#fi 

}
sys_config()
{
cur_time=`date`
echo "------------------------------------------"
echo "Installation started $cur_time"
echo "------------------------------------------"
echo "cli params: "
echo $0 $COMMAND_OPTS
echo "Hostname: `hostname`"
echo "ip list: `ip addr`"
echo ""
command=`uname -a;echo; lsb_release -a`
echo $command 
}

env_validate
sys_config
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


install()
{
    echo "Nothing to done for installation"

}
uninstall()
{
    echo "Nothing to be done for uninstallation "

}
appstart()
{
    echo "Staring app..."
    echo "Not implemented yet.."
}
appstop()
{
    echo "Stopping app..."
    echo "Not implemented yet.."
}
COMMAND=$1
echo "Command is $COMMAND"


case $COMMAND in 
install)
install
;;
uninstall)
uninstall
;;
start)
appstart
;;
stop)
appstop
;;
*)
echo Unsupported Option: "$COMMAND"
usage
;;
esac
