import logging
import subprocess, os
import pytest

import global_var
from btest import exec_cmd, BUILDING_DIR
from global_var import get_value


@pytest.mark.parametrize("group", get_value("group_list"))
@pytest.mark.parametrize("platform", get_value("platform_list"))
@pytest.mark.parametrize("signature", get_value("signature_list"))
@pytest.mark.parametrize("build_type", get_value("type_list"))
def test_shell_building(group, build_type, platform, signature):
    cmd_exec_dir = "{}/{}".format(get_value("BUILDING_DIR"), group)
    cmd_build = "./build-scripts/build-{}.sh -p cix -f debian -b {} -k {} build".format(build_type,
                                                                                        platform,
                                                                                        signature)
    cmd_clean = "./build-scripts/build-{}.sh -p cix -f debian -b {} -k {} clean".format(build_type,
                                                                                        platform,
                                                                                        signature)

    assert exec_cmd(cmd_build, cmd_exec_dir) == 0
    assert exec_cmd(cmd_clean, cmd_exec_dir) == 0


@pytest.mark.parametrize("group", get_value("group_list"))
@pytest.mark.parametrize("platform", get_value("platform_list"))
@pytest.mark.parametrize("signature", get_value("signature_list"))
@pytest.mark.parametrize("build_type", get_value("type_list"))
def test_env_building(group, build_type, platform, signature):
    cmd_exec_dir = "{}/{}".format(BUILDING_DIR, group)
    cmd_config = "'-p cix -f debian -k {} -b {}'".format(signature, platform)
    cmd_source = "./build-scripts/envtool.sh"

    assert exec_cmd("./env_building.sh {} {} {} {}".format(cmd_exec_dir, cmd_source, cmd_config, build_type)) == 0
