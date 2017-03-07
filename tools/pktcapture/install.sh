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
OS_ARCH='x86_64'
LOG_FILE=${PWD##*/}.log
TMP_DIR=tmp
CONFIG_FILE=install.config
COMMAND_OPTS="$@"
DRYRUN=0
WIRESHARK_INSTALL=0
WIRESHARK_VER='0.0.0'

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
} 
#vne::tbd} >> $LOG_FILE 2>&1

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

validate_wireshark()
{
pkg_state=`dpkg --get-selections | grep -w wireshark | head -1| awk {'print $2'}`
if [ $pkg_state = 'install' ]; then 
  echo 'wireshark already installed'
  WIRESHARK_INSTALL=1
else
  echo 'wireshark not already installed'
  WIRESHARK_INSTALL=0
fi
}

install_dissectors()
{

set -x
WIRESHARK_VER=`wireshark -v | grep -w "^wireshark" | awk {'print $2'}`
PLUGIN_DIR='/usr/lib/x86_64-linux-gnu/wireshark/libwireshark3/plugins/'

if [ ! -d $TMP_DIR ]; then
  mkdir $TMP_DIR
fi

if [ ! -d $PLUGIN_DIR ]; then
  echo "Plugin directory: $PLUGIN_DIR does not exist"
  return 1
fi

GD1=`echo $WIRESHARK_VER | cut -f1 -d'.'`
GD2=`echo $WIRESHARK_VER | cut -f2 -d'.'`
ARCH=`arch | cut -f2 -d'_'`
GNAME=generic.so.$ARCH.$GD1${GD2}X.tar.gz
cd dissector/generic
if [ ! -f $GNAME ]; then
   echo "Generic dissector $GNAME does not exist"
   return 1
fi 
cd -
MQTT_DISSECTOR=mqtt_wireshark_generic_dissector.zip
cp dissector/generic/$GNAME $TMP_DIR
cp dissector/mqtt/$MQTT_DISSECTOR $TMP_DIR

cd $TMP_DIR
tar -zxvf $GNAME
unzip $MQTT_DISSECTOR
cp generic.so $PLUGIN_DIR
cp mqtt3* $PLUGIN_DIR
cd -
rm -rf $TMP_DIR
}
get_wireshark()
{
validate_wireshark
#check if it is already installed 
if [ $WIRESHARK_INSTALL = '0' ]; then 
apt-get install -y wireshark
fi
wireshark --version
install_dissectors
}

start_wireshark()
{
  echo "Interfaces available for capture"
  PCAP_FILE='/tmp/out.pcap'
  #enable dumpcap for non-root users
  sudo setcap 'CAP_NET_RAW+eip CAP_NET_ADMIN+eip' /usr/bin/dumpcap
  wireshark -D
  wireshark -kSl -i lo -w $PCAP_FILE
}
install()
{
    echo "Installing..."
    if [ `whoami` != 'root' ]; then 
       echo 'User is not root. Exiting'
       exit 1
    fi 
    get_wireshark

}
uninstall()
{
    echo "Uninstalling..."
    apt-get remove -y wireshark

}

appstart()
{
    echo "Staring app..."
    validate_wireshark
    if [ $WIRESHARK_INSTALL = '1' ]; then
       echo "starting wireshark"
       start_wireshark
    else
       echo 'Wireshark not installed'
    fi
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
echo "Uninstallation complete"
;;
start)
echo "vne::tbd::this needs to be started as non-root"
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
