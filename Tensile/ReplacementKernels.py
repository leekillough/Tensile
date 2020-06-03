################################################################################
# Copyright 2020 Advanced Micro Devices, Inc. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell cop-
# ies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IM-
# PLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNE-
# CTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
################################################################################

from .Common import globalParameters

import os

class ReplacementKernels:
    _instance = None

    def getKernelName(self, filename):
        try:
            with open(filename, 'r') as f:
                for line in f:
                    if line.startswith(self.marker):
                        return line[len(self.marker):].strip()
        except Exception:
            print(filename)
            raise
        raise RuntimeError("Could not parse kernel name from {}".format(filename))

    def __init__(self):
        if self._instance:
            raise RuntimeError("ReplacementKernels constructed more than once")
        self.cache = {}
        cov2 = globalParameters['CodeObjectVersion'] == 'V2'
        self.marker = '.amdgpu_hsa_kernel' if cov2 else '.amdhsa_kernel'
        dirName = 'ReplacementKernels-cov2' if cov2 else 'ReplacementKernels'
        dirPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), dirName)
        for fileName in os.listdir(dirPath):
            if fileName.endswith('.s'):
                filePath = os.path.join(dirPath, fileName)
                kernelName = self.getKernelName(filePath)
                if kernelName in self.cache:
                    raise RuntimeError("Duplicate replacement kernels.  Kernel name: {}, file names: {}, {}".
                                       format(kernelName, self.cache[kernelName], filePath))
                self.cache[kernelName] = filePath
        self._instance = self

    @staticmethod
    def Instance():
        return ReplacementKernels._instance or ReplacementKernels()._instance

    @classmethod
    def Get(cls, kernelName):
        return cls.Instance().cache.get(kernelName)
