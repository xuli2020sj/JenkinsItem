import argparse
import logging
import signal
import subprocess
import time
import cixlogging

REPO_INFO = "ssh://git@gitmirror.cixcomputing.com/linux_repo/cix-manifest -b cix_master"
BUILDING_DIR = "/home/svc.swciuser/building_test/{}".format(time.strftime('%Y%m%d_%H%M%S', time.localtime()))
GIT_SERVER = 'gitmirror.cixtech.com'


# Synchronous execution of cmd
def exec_cmd(command, cmd_dir=""):
    logging.info("Executing cmd {}: {}".format(cmd_dir, command))
    if cmd_dir == "":
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, close_fds=True)
    else:
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cmd_dir, close_fds=True)

    out, err_out = p.communicate()

    if p.returncode != 0:
        logging.error(err_out)
    else:
        logging.info(out)
    return p.returncode


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


def repo_sync():
    for group in group_list:
        exec_cmd("mkdir -p {}".format("{}/{}".format(BUILDING_DIR, group)))
        cmd_exec_dir = "{}/{}".format(BUILDING_DIR, group)
        cmd_init_repo = "repo init --depth 1 -u {} -g cix,{} -m release/{}/default.xml".format(REPO_INFO, group, release)
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='build test', description='Do building test. ')
    parser.add_argument('--release', '-r', required=True, type=str, help='Give the target release to test like '
                                                                         'cix_sky1_Alpha0.4-rc1.'
                        , choices=['cix_sky1_Alpha0.4-rc1'], default=['cix_sky1_Alpha0.4-rc1'])
    parser.add_argument('--way', '-w', required=False, type=str, help='Give the buid way like shell or env or all for '
                                                                      'all possible way'
                        , choices=['shell', 'env']
                        , action='append', default=['shell', 'env'])
    parser.add_argument('--group', '-g', required=False, type=str, help='Give the code group like private, cix, sec '
                                                                        'or all for all groups'
                        , choices=['cix', 'private', 'sec'], action='append', default=['cix', 'private', 'sec'])
    parser.add_argument('--platform', '-p', required=False, type=str, help='Give the platform to build like fpga, '
                                                                           'emu, sky1 or all for all possible '
                                                                           'platforms'
                        , choices=['emu', 'fpga']
                        , action='append', default=['emu', 'fpga'])
    parser.add_argument('--signature', '-k', required=False, type=str, help='Give the signature way like sm2 or rsa '
                                                                            'or all for all possible platforms'
                        , choices=['rsa', 'sm2'], action='append', default=['rsa', 'sm2'])
    parser.add_argument('--type', '-t', required=False, type=str, help='Give the build type like minimum, all or full '
                                                                       'for all possible values.'
                        , choices=['all', 'minimum'], action='append', default=['all', 'minimum'])
    args = parser.parse_args()

    release = args.release
    way_list = args.way
    group_list = args.group
    platform_list = args.platform
    signature_list = args.signature
    type_list = args.type

    signal.signal(signal.SIGINT, quit_clean)
    signal.signal(signal.SIGALRM, quit_clean)

    logging.info("Building dir is: {}".format(BUILDING_DIR))

    repo_sync()
    for way in way_list:
        if way == "shell":
            shell_build()
        elif way == "env":
            env_build()
