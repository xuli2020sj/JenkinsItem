#!/usr/bin/env python3

import pexpect
import sys
import os

prt = "Password:"
cmdBase = "scp %s svc.fpgatest@fpga05.cixcomputing.cn:%s" % (sys.argv[1], sys.argv[2])
mkcmd = "\"mkdir -p %s\"" % os.path.dirname(sys.argv[2])

# mkdir
cid = pexpect.spawn("ssh svc.fpgatest@fpga05.cixcomputing.cn " + mkcmd, encoding='utf-8', codec_errors='replace')
cid.logfile = sys.stdout
cid.expect(prt)
# send password
cid.sendline("Cix@88008080")
cid.expect([pexpect.EOF, pexpect.TIMEOUT])

cid = pexpect.spawn(cmdBase, encoding='utf-8', codec_errors='replace')
cid.logfile = sys.stdout
cid.expect(prt)
# send password
cid.sendline("Cix@88008080")
cid.expect(['\$', pexpect.EOF], timeout=60)
