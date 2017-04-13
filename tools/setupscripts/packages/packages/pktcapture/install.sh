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
    OS_STR_DELIM=","
    OS_MATCHED="False"

    if [ ! -f $CONFIG_FILE ]; then
        echo ' $CONFIG_FILE does not exist. Incomplete installation. Exiting'
        exit 1
    fi

    USER=`users | awk {'print $1'}`
    SUPPORTED_OS=`cat $CONFIG_FILE | grep '^os' | cut -f2 -d"$DELIM"`
    target_os=`lsb_release -a | grep Distributor | awk {'print $3'}`
    
    echo "supported os are:"
    IFS=$OS_STR_DELIM
    for OS in $SUPPORTED_OS
    do
        echo "$OS"
        if [ $target_os = $OS ]; then
            OS_MATCHED="TRUE"
            break;
        fi
    done

    if [ $OS_MATCHED = "TRUE" ]; then
        echo "Mached OS is $OS"
    else
        echo "Target OS version: $target_os not supported. Exiting."
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
if [[ ($pkg_state) && ($pkg_state = 'install') ]]; then 
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

get_prerequisite_package()
{
   pkg_state=`dpkg --get-selections | grep -w wmctrl | head -1| awk {'print $2'}`
   if [[ ($pkg_state) && ($pkg_state = 'install') ]]; then 
      echo 'wmctrl is already installed'
   else
      echo 'Installing wmctrl'
      sudo apt-get install -y wmctrl
   fi
   wmctrl --version
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

get_Interface_and_filter()
{
   DELIM=":"
   CAP_IFACE=`cat $CONFIG_FILE | grep -w "^wsinf" | cut -f2 -d"$DELIM"`
   CAP_FILTER=`cat $CONFIG_FILE | grep -w "^wsfilter" | cut -f2 -d"$DELIM"`
}

start_wireshark()
{
  echo "Interfaces available for capture"
  PCAP_FILE='/tmp/out.pcap'
  #enable dumpcap for non-root users
  sudo setcap 'CAP_NET_RAW+eip CAP_NET_ADMIN+eip' /usr/bin/dumpcap

  get_Interface_and_filter

  set -x
  #/bin/su - $USER /bin/bash -c "wireshark -D;wireshark -kSl -i $CAP_IFACE -f $CAP_FILTER -w $PCAP_FILE&"
  #/bin/su - $USER /bin/bash -c "wireshark -D;wireshark -kSl -i $CAP_IFACE -f $CAP_FILTER&"
  /bin/su - $USER /bin/bash -c "wireshark -D;env DISPLAY=:0 XAUTHORITY=/home/$USER/.Xauthority wireshark -kSl -i $CAP_IFACE -f $CAP_FILTER&"

  sleep 10
  #METHOD:1
  #winid=`xwininfo -name wireshark |grep "Window id" |awk {'print $4'}`
  #wmctrl -i $winid -b add,fullscreen

  #METHOD:2
  #wmctrl -r wireshark -b add,fullscreen
  env DISPLAY=:0 XAUTHORITY=/home/$USER/.Xauthority wmctrl -r "wireshark" -b add,fullscreen
  set +x

  #To remove fullscreen
  #wmctrl -r wireshark -b remove,fullscreen
}

install()
{
    echo "Installing..."
    if [ `whoami` != 'root' ]; then 
       echo 'User is not root. Exiting'
       exit 1
    fi
    get_prerequisite_package 
    get_wireshark

}
uninstall()
{
    echo "Uninstalling..."
    apt-get remove -y wireshark
    apt-get remove -y wmctrl

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
    kill -9 `ps -ef | grep wireshark | grep -v grep | awk {'print $2'}`
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
