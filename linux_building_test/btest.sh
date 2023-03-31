#!/bin/bash
#copyright (C) 2023 CIX Technology, Inc. All Rights Reserved.
#
# The code contained herein is licensed under the GNU General Public
# License. You may obtain a copy of the GNU General Public License
# Version 2 or later at the following locations:
#
# http://www.opensource.org/licenses/gpl-license.html
# http://www.gnu.org/copyleft/gpl.html
##############################################################################
#
# Revision History:
#                       Modification     Tracking
# Author                    Date          Number    Description of Changes
#--------------------   ------------    ----------  ---------------------
# Anthony Tian          02/13/2023       n/a         Initial Version
#############################################################################
# File Name:     btest.sh
# Total Tests:   1
# Description:   Do building test. 

# args:
# arg1: -w way           Give the buid way like shell or env or all for all possible way
# arg2: -t group         Give the code group like private, cix, sec or all for all groups
# arg3: -p platform      Give the platform to build like fpga, emu, sky1 or all for all possible platforms
# arg4: -k signature     Give the signature way like sm2 or rsa or all for all possible platforms
# arg5: -t type          Give the build type like minimum, all or full for all possible values.
# arg6: -r release       Give the target release to test like cix_sky1_Alpha0.4-rc1. It is mandatory.
# if no args, value for arg1-arg5 are full

# Function:    usage
#
# Description: - Display the help info.
# Return:      - 1

usage()
{
    cat <<-EOF

    File Name:     btest.sh
    Total Tests:   1
    Description:   Do building test. 

    args:
    arg1: -w way           Give the buid way like shell or env or full for all possible way.
    arg2: -g group         Give the code group like private, cix, sec or full for all groups.
    arg3: -p platform      Give the platform to build like fpga, emu, sky1 or full for all possible platforms.
    arg4: -k signature     Give the signature way like sm2 or rsa or full for all possible platforms.
    arg5: -t type          Give the build type like minimum, all or full for all possible values.
    arg6: -r release       Give the target release to test like cix_sky1_Alpha0.4-rc1. It is mandatory.

    if no args, value for arg1-arg5 are full

EOF
    exit 1
}

# Function:     setup
#
# Description:  - Check if required commands exits
#               - Parse args and export global variables
#               - Check if required config files exits
#               - Create temporary files and directories
#
# Return        - zero on success
#               - 1 on failure. return value from commands ($RC)
setup()
{
    # Initialize return code to zero.
    RC=0                 # Exit values of system commands used

    TST_TOTAL=1   # Total number of test cases in this file.
    LTPTMP=${TMP}        # Temporary directory to create files, etc.
    TST_COUNT=0   # Set up is initialized as test 0

    repInfo="ssh://git@gitmirror.cixcomputing.com/linux_repo/cix-manifest -b cix_master"

    wayList="shell env"
    grpList="cix private sec"
    pltList="emu fpga"
    sgnList="rsa sm2"
    typList="all minimum"
    
    # build directory
    bDir=~/btest/`date +%Y%m%d_%H%M%S_%N |cut -b1-20`
    mkdir -p $bDir/logs
    fList=$bDir/logs/flist.txt

    # trap signal
    trap "cleanup" 0

    # Parse args
    while [ $# -ne 0 ];do
        OPTIND=0
        while getopts w:g:p:k:t:r: arg
        do
            case $arg in
                w) if [ $OPTARG != "full" ]; then wayList=$OPTARG; fi;;
                g) if [ $OPTARG != "full" ]; then grpList=$OPTARG; fi;;
                p) if [ $OPTARG != "full" ]; then pltList=$OPTARG; fi;;
                k) if [ $OPTARG != "full" ]; then sgnList=$OPTARG; fi;;
                t) if [ $OPTARG != "full" ]; then typList=$OPTARG; fi;;
                r) rInfo=$OPTARG;;
                \?|h) usage;;
            esac
       done

       if [ $OPTIND -ne $(($#+1)) ]
       then
           shift $(($OPTIND-1))
           FILE_DIR="$FILE_DIR $1"
           shift
       else
           break
       fi
   done

   if [ -z "$rInfo" ]; then
       echo "'-r release' option is mandatory"
       exit 1
   fi

   echo $RC > $bDir/logs/rc.value

   return $RC

}

# Function:     crv
#
# Description   - change RC's value
#
# Return        - zero on success
#               - non zero on failure. return value from commands ($RC)
crv()
{
    rcf=$bDir/logs/rc.value
    curV=`cat $rcf`
    let newV=curV+1
    echo $newV > $rcf
}

# Function:     ufl 
#
# Description   - update fail list
#
# Return        - zero on success
#               - non zero on failure. return value from commands ($RC)
ufl()
{
    echo "$@" >> $fList
}

# Function:     cleanup
#
# Description   - remove temporary files and directories.
#
# Return        - zero on success
#               - non zero on failure. return value from commands ($RC)
cleanup()
{
    RC=0
    #echo "In Cleanup"
    return $RC
}

# Function:     repo sync
#
# Description:  do code repo sync
#
# Exit:         zero on success
#               non-zero on failure.
#
repoOP()
{
    for grp in $grpList; do
        mkdir $bDir/$grp
        cd $bDir/$grp
        repo init -u $repInfo \
            -g cix,$grp -m release/$rInfo/default.xml || { \
            crv; \
            echo "repo init fails for group: $grp and release: $rInfo"; \
            ufl "repo init fails for group: $grp and release: $rInfo"; \
        }
        repo sync || { \
            crv; \
            echo "repo sync fails for group: $grp and release: $rInfo"; \
            ufl "repo sync fails for group: $grp and release: $rInfo"; \
        }
    done
}

# Function:     sbuild()
#
# Description:  shell way to do building
#
# Exit:         zero on success
#               non-zero on failure.
#
sbuild()
{
    for grp in $grpList; do
        cd $bDir/$grp
        for plt in $pltList; do
            for sgn in $sgnList; do
                for typ in $typList; do
                    # build
                    { bash ./build-scripts/build-${typ}.sh -p cix -f debian -b $plt -k $sgn build || { \
                        crv; \
                        echo "build fails for group: $grp, release: $rInfo, platform:$plt, signature: $sgn"; \
                        ufl "build fails for group: $grp, release: $rInfo, platform:$plt, signature: $sgn"; \
                        }; \
                    } 2>&1 | tee shb_${grp}_${plt}_${typ}_${sgn}.log
                    cp shb_${grp}_${plt}_${typ}_${sgn}.log $bDir/logs
                    # Todo: build output check

                    # clean
                    { bash ./build-scripts/build-${typ}.sh -p cix -f debian -b $plt -k $sgn clean || { \
                        crv; \
                        echo "clean fails for group: $grp, release: $rInfo, platform:$plt, signature: $sgn"; \
                        ufl "clean fails for group: $grp, release: $rInfo, platform:$plt, signature: $sgn"; \
                        }; \
                    } 2>&1 | tee shc_${grp}_${plt}_${typ}_${sgn}.log
                    cp shc_${grp}_${plt}_${typ}_${sgn}.log $bDir/logs
                    # Todo: clean result check
                done
            done
        done
    done
}

# Function:     ebuild()
#
# Description:  env way to do building
#
# Exit:         zero on success
#               non-zero on failure.
#
ebuild()
{
    for grp in $grpList; do
        cd $bDir/$grp
        { . ./build-scripts/envtool.sh || { \
            crv; \
            echo "source envtool fails for group: %grp and release: %rInfo"; \
            ufl "source envtool fails for group: %grp and release: %rInfo"; \
            }; \
        } 2>&1 | tee env_${grp}.log
        # source again to make sure env is working
        . ./build-scripts/envtool.sh
        cp env_${grp}.log $bDir/logs
        for plt in $pltList; do
            for sgn in $sgnList; do
                for typ in $typList; do
                    # build
                    config -p cix -f debian -k $sgn -b $plt | tee env_${grp}_${plt}_${typ}_${sgn}.log
                    cp env_${grp}_${plt}_${typ}_${sgn}.log $bDir/logs
                    { build $typ || { \
                        crv; \
                        echo "build fails for group: $grp, release: $rInfo, platform:$plt, signature: $sgn"; \
                        ufl "build fails for group: $grp, release: $rInfo, platform:$plt, signature: $sgn"; \
                        }; \
                    } 2>&1 | tee eb_${grp}_${plt}_${typ}_${sgn}.log
                    cp eb_${grp}_${plt}_${typ}_${sgn}.log $bDir/logs
                    # To do: build output check

                    # clean
                    { clean $typ || { \
                        crv; \
                        echo "clean fails for group: $grp, release: $rInfo, platform:$plt, signature: $sgn"; \
                        ufl "clean fails for group: $grp, release: $rInfo, platform:$plt, signature: $sgn"; \
                        }; \
                    } 2>&1 | tee ec_${grp}_${plt}_${typ}_${sgn}.log
                    cp ec_${grp}_${plt}_${typ}_${sgn}.log $bDir/logs
                    # To do: clean result check

                done
            done
        done
    done
}

# main
#
# Description:  - Execute all tests, exit with test status.
#
# Exit:         - zero on success
#               - non-zero on failure.
#
RC=0    # Return value from setup, and test functions.

#"" will pass the whole args to function setup()
setup "$@" || exit $RC
repoOP
for way in $wayList; do
    if [ $way == "shell" ]; then
        sbuild
    elif [ $way == "env" ]; then
        ebuild
    fi
done
RC=`cat $bDir/logs/rc.value`
if [ $RC -ne 0 ]; then
    echo "Build test fails, Please check the logs"
fi
exit $RC
