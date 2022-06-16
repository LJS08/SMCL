# coding:utf-8
# Make a SMCL dir if there is no.

import os


def makeDir():
    if not os.path.isdir("./SMCL"):
        os.mkdir("./SMCL")
