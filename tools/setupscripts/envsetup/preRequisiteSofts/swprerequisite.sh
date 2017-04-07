# !/bin/bash

########################################################################
#                                                                      #
# This script will be used for install dependent package on the system #
#                                                                      #
########################################################################

# Global variables
dPkage=''
DLIM="-"
instHistory=' '
INSTALLED_LOG_FILE=installed.log
TMP_FILE=temp
PRE_PACKAGE_LIST=prePkgList.txt

#set -x
# Creating backup of log file and removes old backup log file
manage_logFiles()
{
    LOG_PRESENT=`ls | grep -w $INSTALLED_LOG_FILE | head -1`
    if [ $LOG_PRESENT ]; then
        BCKP_PRESENT=`ls | grep -w $INSTALLED_LOG_FILE.bckp | head -1`
        if [ $BCKP_PRESENT ]; then
            rm $INSTALLED_LOG_FILE.bckp
        fi
        mv $INSTALLED_LOG_FILE $INSTALLED_LOG_FILE.bckp
    fi
}

install_dependent_package()
{
    echo
    echo "$dPkage =>"
    echo "Checking for previous installation..."
    pkgState=`dpkg --get-selections | grep -w ^$dPkage -m 1 | awk {'print $2'}`
    if [[ ($pkgState) && ($pkgState = 'install') ]]; then
        echo "\"$dPkage\" is already installed."
        instHistory="Legacy"
    else
        echo "No previous installation found for $dPkage"
        echo "Installing $dPkage ..."
        sudo apt-get install -y $dPkage
        echo "\"$dPkage\" has been installed successfully."
        instHistory="New"
    fi
    ver=`apt-cache show $dPkage | grep Version | cut -f1 -d$DLIM | awk {'print $2'}`
    echo "Version: $ver"
    echo -e "$dPkage \t$ver \tinstalled\t$instHistory">>$TMP_FILE
    echo "-----------------------------------------------------------------"
}

uninstall_dependent_package()
{
    echo "Uninstalling the \"$uPkage\""
    echo
    sudo apt-get remove -y $uPkage

}

#######################################################################
#                   Package installation from System                  #
#######################################################################

install_packages()
{
    manage_logFiles
    echo
    echo "===================== Installing required packages ======================"
    while read -a line
    do
        dPkage=`echo -e "${line[0]}"`
        echo -e "Package Name: \"${line[0]}\""
        install_dependent_package
        echo
    done <"$PRE_PACKAGE_LIST"

    # Generating package log file
    column -t $TMP_FILE>$INSTALLED_LOG_FILE
    \rm $TMP_FILE
}

#######################################################################
#               Package uninstallation from System                    #
#######################################################################
#uPkage=sl
#uninstall_dependent_package

uninstall_package()
{
    echo
    echo "=========================== Removing packages ==========================="
    while read -a line
    do
        uPkage=${line[0]}
        echo
        echo -e "$uPkage =>"
        instHistory=${line[3]}
        if [ $instHistory = "New" ]; then
            uninstall_dependent_package
        else
            echo "$uPkage is a Legacy package. So, Not removed."
        fi
        echo "-----------------------------------------------------------------"
    done <"$INSTALLED_LOG_FILE"
}

################################ MAIN ########################################
while true
do
    case "$1" in
    -h | --help)
    usage
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

usage()
{
    echo "Usage: $0 [params] install|uninstall"
    echo "params can be one of following:"
    echo "    --help | -h        : Print out this help message"
    exit 1
}

COMMAND=$1
echo "Command is $COMMAND"

case $COMMAND in 
install)
install_packages
;;
uninstall)
uninstall_package
;;
*)
echo Unsupported Option: "$COMMAND"
usage
;;
esac
