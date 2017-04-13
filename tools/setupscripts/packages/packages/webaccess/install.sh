# !/usr/bin/bash 

#vne::tbds
## Uninstall functionality
#pwd authentication in novnc
#https support in webserver, tty and novnc
#wireshark functionality 

#check if sshd service running or not
#cleanup function 
#service and configuration persistence
####################################################

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
if [ ! -f $tty_configjson ]; then 
  echo "$tty_configjson does not exist. Incomplete installation. Exiting"
  exit 1
fi 

OS=`cat $CONFIG_FILE | grep '^os' | cut -f2 -d"$DELIM"`
#os_ver=`uname -a | awk {'print $2'}`
os_ver=`lsb_release -a | grep '^Distributor' | awk {'print $3'}`
echo "Suported OS: $OS, Target OS: $os_ver"
if [ $os_ver != $OS ] ; then
  echo "OS version: $os_ver not supported. Exiting."
  exit 1
fi 

if [ `whoami` != 'root' ]; then 
  echo 'User is not root. Exiting'
  exit 1
fi 

}
############ MULTIPLE OS SUPPORT FROM CONFIG ##################
## below code is working with pktcapture package ##############
### here TBD: replace it with above function ##################
<<'TBD'
env_validate()
{
#set -x
    DELIM=":"
    OS_STR_DELIM=","
    OS_MATCHED="False"

    if [ ! -f $CONFIG_FILE ]; then
        echo ' $CONFIG_FILE does not exist. Incomplete installation. Exiting'
        exit 1
    fi 
    
    if [ ! -f $tty_configjson ]; then 
        echo "$tty_configjson does not exist. Incomplete installation. Exiting"
        exit 1
    fi 

    SUPPORTED_OS=`cat $CONFIG_FILE | grep '^os' | cut -f2 -d"$DELIM"`
    target_os=`lsb_release -a | grep Distributor | awk {'print $3'}`
    echo "Supported os are:"
    
    IFS=$OS_STR_DELIM
    for OS in $SUPPORTED_OS
    do
        echo "$OS"
        if [ $target_os = $OS ]; then
            OS_MATCHED="TRUE"
            break;
        fi
    done

    if [ $OS_MATCHED = 'TRUE' ]; then
        echo "Mached OS is $OS"
    else
        echo "Target OS version: $target_os not supported. Exiting."
        exit 1
    fi

    if [ `whoami` != 'root' ]; then 
        echo 'User is not root. Exiting'
        exit 1
    fi 
}
TBD
############ MULTIPLE OS SUPPORT FROM CONFIG END ###############
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

config_file=webaccess.config
#Config file for tty.js module
tty_configjson=ttyconfig.json
ip_token='ip_address'
port_token='port'

echo "envset: $envset"
if [[ ($envset) && ($envset = 'true') ]]; then
  echo "env ip: $envip and port: $envport set successfully."
  ipaddr=$envip
  port=$envport
else
  echo "Taking default ip and port from $config_file"
  ipaddr=`cat $config_file | grep $ip_token | awk {'print $3'}`
  port=`cat $config_file | grep $port_token | awk {'print $3'}`
fi
ttyport=`expr $port + 1`
novncport=`expr $ttyport + 1`
vncport=`expr $novncport + 1`

dfile='.install'
dipaddr='127.0.0.1'
dport=8000
dttyport=`expr $dport + 1`
dnovncport=`expr $dttyport + 1`
validate_network_params()
{
ip addr | grep $ipaddr
if [ $? -eq 0 ]; then
echo "ip address: $ipaddr exists"
else
echo "ip address: $ipaddr not present in system. Invalid config"
exit 1
fi
netstat -anp | grep $port
if [ $? -eq 0 ]; then
echo "Web Server port number: $port already in use. Exiting."
exit 1
fi
netstat -anp | grep $ttyport
if [ $? -eq 0 ]; then
echo "TTY port number: $ttyport already in use. Exiting."
exit 1
fi
netstat -anp | grep $vncport
if [ $? -eq 0 ]; then
echo "VNC port number: $vncport already in use. Exiting."
exit 1
fi
netstat -anp | grep $novncport
if [ $? -eq 0 ]; then
echo "No VNC port number: $novncport already in use. Exiting."
exit 1
fi
}

get_config_bkup()
{
if [ -f $dfile ]; then
dipaddr=`cat $dfile | cut -d':' -f1` 
dport=`cat $dfile | cut -d':' -f2` 
dttyport=`cat $dfile | cut -d':' -f3` 
dnovncport=`cat $dfile | cut -d':' -f4` 
fi
echo "dconfig details"
echo $dipaddr $dport $dttyport $dnovncport
}
dump_config_bkup()
{
if [ ! -f $dfile ]; then
echo "first time installation" 
else
echo "installation already done"
fi 
echo $ipaddr:$port:$ttyport:$novncport > $dfile 
}
install_nodejs_modules()
{
#set -x
pkg_state=`dpkg --get-selections | grep nodejs | awk {'print $2'}`
if [[ ($pkg_state) && ($pkg_state = 'install') ]]; then 
  echo 'nodejs already installed'
else
   curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
   apt-get install -y nodejs 
   echo 'nodejs installed'
fi
echo "Node Js: `node -v`"
echo "NPM : `npm -v`"
echo 'installing required nodejs modules'
node_mods='tty.js bluebird'
npm install $node_mods
}
params_replace()
{
js_file='app.js'
html_file='index.html'
get_config_bkup
sed -i -e 's/'"$dipaddr"'/'"$ipaddr"'/g' $js_file
sed -i -e 's/'"$dport"'/'"$port"'/g' $js_file

#set -x
sed -i -e 's/'"$dipaddr"'/'"$ipaddr"'/g' $html_file
sed -i -e 's/'"$dttyport"'/'"$ttyport"'/g' $html_file
sed -i -e 's/'"$dnovncport"'/'"$novncport"'/g' $html_file
#set +x
sed -i -e 's/'"$dttyport"'/'"$ttyport"'/g' $tty_configjson
dump_config_bkup
}


###### x11vnc installation ########
install_x11vnc()
{
pkg_state=`dpkg --get-selections | grep x11vnc | awk {'print $2'} | head -1`
if [[ ($pkg_state) && ($pkg_state = 'install') ]]; then 
  echo 'x11vnc already installed'
else
  apt-get install -y x11vnc
fi 
echo "x11vnc version: `x11vnc --version`" 
}

install_novnc()
{
if [ -d "noVNC" ]; then
echo "noVNC already present at:"
echo "$PWD"
else
echo "noVNC is installed at: $PWD"
git clone git://github.com/kanaka/noVNC
fi
}

final_print()
{
echo "-----------------------------------------------------------"
echo "Webserver running at: http://$ipaddr:$port"
echo "Web Console Access running at: http://$ipaddr:$ttyport"
echo "NoVNC Desktop Access URL: "
echo "http://$ipaddr:$novncport/vnc.html"
echo "-----------------------------------------------------------"
}

start_nodejs_server()
{
echo "Starting nodejs application"
node app.js &
}
start_vnc_server()
{
echo "starting x11vnc server"
#/usr/bin/x11vnc -xkb -auth /var/run/lightdm/root/:0 -noxrecord -noxfixes -noxdamage -rfbauth /etc/x11vnc.pass -forever -bg -rfbport $vncport -o /var/log/x11vnc.log
#without password
/usr/bin/x11vnc -xkb -auth /var/run/lightdm/root/:0 -noxrecord -noxfixes -noxdamage -forever -bg -rfbport $vncport -o /var/log/x11vnc.log
}
start_novnc_server()
{
echo "starting novnc"
echo $PWD
./noVNC/utils/launch.sh --vnc localhost:$vncport --listen $novncport &
}
stop_services()
{
kill -9 `ps -ef | grep app.js | grep -v grep | awk {'print $2'}`
kill -9 `ps -ef | grep x11vnc | grep -v grep | awk {'print $2'}`
kill -9 `ps -ef | grep launch.sh | grep -v grep | awk {'print $2'}`
kill -9 `ps -ef | grep websockify | awk {'print $2'}`

}
start_services()
{
  stop_services
  start_vnc_server
  start_novnc_server
  start_nodejs_server
}

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
#set -x
   echo "Installing..."
   validate_network_params
   install_nodejs_modules
   params_replace
   install_x11vnc
   install_novnc
   final_print
   echo "Installation complete"
   echo "-----------------------------------------------------------"
   echo "Webserver running at: http://$ipaddr:$port"
   echo "-----------------------------------------------------------"
}

uninstall()
{
    echo "Uninstalling..."
    echo "vne::tbd:: not implemented yet :("

}
appstart()
{
    echo "Staring app..."
    start_services
}
appstop()
{
    echo "Stopping app..."
    stop_services
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
