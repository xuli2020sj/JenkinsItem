import argparse
import logging
import signal
import subprocess
import time
import cixlogging
import pytest

REPO_INFO = "ssh://git@gitmirror.cixcomputing.com/linux_repo/cix-manifest -b cix_master"
BUILDING_DIR = "/home/svc.swciuser/building_test/{}".format(time.strftime('%Y%m%d_%H%M%S', time.localtime()))
GIT_SERVER = 'gitmirror.cixtech.com'


# Synchronous execution of cmd
def exec_cmd(command, cmd_dir=""):
    logging.info("Executing cmd {}: {}".format(cmd_dir, command))
    if cmd_dir == "":
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, close_fds=True)
    else:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cmd_dir,
                                close_fds=True)

    try:
        outs, errs = proc.communicate()
    except Exception as e:
        logging.error("error {}".format(e))
        proc.kill()
        outs, errs = proc.communicate()

    logging.error(errs)
    logging.info(outs)
    return proc.returncode


def quit_clean():
    """
    This is a groups style docs.

    Parameters:
     param1 - this is the first param
     param2 - this is a second param

    Returns:
     This is a description of what is returned

    Raises:
     KeyError - raises an exception
    """
    pass


def repo_sync(is_release):
    for group in group_list:
        exec_cmd("mkdir -p {}".format("{}/{}".format(BUILDING_DIR, group)))
        cmd_exec_dir = "{}/{}".format(BUILDING_DIR, group)
        if is_release:
            cmd_init_repo = "repo init --depth 1 -u {} -g {} -m release/{}/default.xml".format(REPO_INFO, group,
                                                                                               release)
        else:
            cmd_init_repo = "repo init --depth 1 -u {} -g {} -m default.xml".format(REPO_INFO, group,
                                                                                    )
        cmd_sync_repo = "repo sync -j 32 --force-sync --force-remove-dirty -c --no-tags --no-clone-bundle"

        exec_cmd(cmd_init_repo, cmd_exec_dir)
        exec_cmd(cmd_sync_repo, cmd_exec_dir)


def shell_build():
    for group in group_list:
        for platform in platform_list:
            for signature in signature_list:
                for build_type in type_list:
                    cmd_exec_dir = "{}/{}".format(BUILDING_DIR, group)
                    cmd_build = "./build-scripts/build-{}.sh -p cix -f debian -b {} -k {} build".format(build_type,
                                                                                                        platform,
                                                                                                        signature)
                    cmd_clean = "./build-scripts/build-{}.sh -p cix -f debian -b {} -k {} clean".format(build_type,
                                                                                                        platform,
                                                                                                        signature)

                    exec_cmd(cmd_build, cmd_exec_dir)
                    exec_cmd(cmd_clean, cmd_exec_dir)


def env_build():
    for group in group_list:
        cmd_exec_dir = "{}/{}".format(BUILDING_DIR, group)
        exec_cmd(". ./build-scripts/envtool.sh", cmd_exec_dir)
        for platform in platform_list:
            for signature in signature_list:
                for build_type in type_list:
                    cmd_config = "config -p cix -f debian -k {} -b {}".format(signature, platform)
                    cmd_build = "build {}".format(build_type)
                    cmd_clean = "clean {}".format(build_type)
                    exec_cmd(cmd_config, cmd_exec_dir)
                    exec_cmd(cmd_build, cmd_exec_dir)
                    exec_cmd(cmd_clean, cmd_exec_dir)


def fill_all():
    global release, way_list, group_list, platform_list, signature_list, type_list
    release = ['cix_sky1_Alpha0.4-rc1']
    way_list = ['shell', 'env']
    group_list = ['cix', 'cix,private', 'cix,sec']
    platform_list = ['emu', 'fpga']
    signature_list = ['rsa', 'sm2']
    type_list = ['all', 'minimum']





if __name__ == '__main__':

    signal.signal(signal.SIGINT, quit_clean)
    signal.signal(signal.SIGALRM, quit_clean)

    parser = argparse.ArgumentParser(prog='build test', description='Do building test. ')
    parser.add_argument('--release', '-r', required=True, type=str, help='Give the target release to test like '
                                                                         'cix_sky1_Alpha0.4-rc1.'
                        , choices=['cix_sky1_Alpha0.4-rc1'], action='append')
    parser.add_argument('--way', '-w', required=True, type=str, help='Give the build way like shell or env or all for '
                                                                     'all possible way'
                        , choices=['shell', 'env'], action='append')
    parser.add_argument('--group', '-g', required=True, type=str, help='Give the code group like private, cix, sec '
                                                                       'or all for all groups'
                        , choices=['cix', 'cix,private', 'cix,sec'], action='append')
    parser.add_argument('--platform', '-p', required=True, type=str, help='Give the platform to build like fpga, '
                                                                          'emu, sky1 or all for all possible '
                                                                          'platforms'
                        , choices=['emu', 'fpga'], action='append')
    parser.add_argument('--signature', '-s', required=True, type=str, help='Give the signature way like sm2 or rsa '
                                                                           'or all for all possible platforms'
                        , choices=['rsa', 'sm2'], action='append')
    parser.add_argument('--type', '-t', required=True, type=str, help='Give the build type like minimum, all or full '
                                                                      'for all possible values.'
                        , choices=['all', 'minimum'], action='append')
    parser.add_argument('--all', '-a', required=False, type=bool, help='Choose whether to test all building'
                        , default=False)
    args = parser.parse_args()

    release = args.release
    way_list = args.way
    group_list = args.group
    platform_list = args.platform
    signature_list = args.signature
    type_list = args.type
    choose_all = args.all

    if choose_all:
        fill_all()

    logging.info("Building dir is: {}".format(BUILDING_DIR))
    logging.info("type_list is: {}".format(type_list))
    logging.info("group_list is: {}".format(group_list))
    logging.info("way_list is: {}".format(way_list))
    logging.info("platform_list is: {}".format(platform_list))
    logging.info("signature_list is: {}".format(signature_list))

    repo_sync(False)
    for way in way_list:
        if way == "shell":
            shell_build()
        elif way == "env":
            env_build()
