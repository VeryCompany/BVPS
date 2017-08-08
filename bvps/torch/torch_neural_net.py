# Copyright 2015-2016 Carnegie Mellon University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This file is Vitalius Parubochyi's modification of `torch_neural_net.py`
# to use lutorpy instead of calling a Lua subprocess.
# It's currently not used by default to avoid adding an
# additional dependency.
# More details are available on this mailing list thread:
# https://groups.google.com/forum/#!topic/cmu-openface/Jj68LJBdN-Y
"""Module for Torch-based neural network usage."""

import lutorpy as lua
import numpy as np
import binascii
import cv2
import os
import logging as log

torch = lua.require('torch')
nn = lua.require('nn')
dpnn = lua.require('dpnn')
image = lua.require('image')

myDir = os.path.dirname(os.path.realpath(__file__))


class TorchNeuralNet:
    """Use a `Torch <http://torch.ch>` and `Lutorpy <https://github.com/imodpasteur/lutorpy>`."""

    #: The default Torch model to use.
    defaultModel = os.path.join(myDir, '..', 'models', 'openface',
                                'nn4.small2.v1.t7')
    def __init__(self, model=defaultModel, imgDim=96, cuda=False):
        """__init__(self, model=defaultModel, imgDim=96, cuda=False)

        Instantiate a 'TorchNeuralNet' object.

        :param model: The path to the Torch model to use.
        :type model: str
        :param imgDim: The edge length of the square input image.
        :type imgDim: int
        :param cuda: Flag to use CUDA in the subprocess.
        :type cuda: bool
        """
        assert model is not None
        assert imgDim is not None
        assert cuda is not None

        torch.setdefaulttensortype('torch.FloatTensor')

        self._net = torch.load(model)
        self._net.evaluate(self._net)

        self._tensor = torch.Tensor(1, 3, imgDim, imgDim)
        self._cuda_tensor = None
        if cuda:
            cutorch = lua.require('cutorch')
            lua.require('cunn')
            self._net = self._net._cuda()
            cutorch.setDevice(2)
            self._cuda_tensor = torch.CudaTensor(1, 3, imgDim, imgDim)
        self._cuda = cuda
        self._imgDim = imgDim
        log.info("run recognize with GPU: {}".format(cuda))

    def forward(self, rgbImg):
        """
        Perform a forward network pass of an RGB image.

        :param rgbImg: RGB image to process. Shape: (imgDim, imgDim, 3)
        :type rgbImg: numpy.ndarray
        :return: Vector of features extracted from the neural network.
        :rtype: numpy.ndarray
        """
        assert rgbImg is not None
        rgbImg_norm = (np.float32(rgbImg)) / 255
        r, g, b = cv2.split(rgbImg_norm)

        if self._cuda:
            self._cuda_tensor[0][0] = torch.fromNumpyArray(r)
            self._cuda_tensor[0][1] = torch.fromNumpyArray(g)
            self._cuda_tensor[0][2] = torch.fromNumpyArray(b)
            rep = self._net._forward(self._cuda_tensor)._float()
        else:
            self._tensor[0][0] = torch.fromNumpyArray(r)
            self._tensor[0][1] = torch.fromNumpyArray(g)
            self._tensor[0][2] = torch.fromNumpyArray(b)
            rep = self._net.forward(self._net, self._tensor)
        rep = rep.asNumpyArray().astype(np.float64)
        return rep
