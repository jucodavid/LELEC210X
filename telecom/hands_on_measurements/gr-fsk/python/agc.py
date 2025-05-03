#!/usr/bin/env python
#
# Copyright 2021 UCLouvain.
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#


from distutils.version import LooseVersion

import numpy as np
from gnuradio import gr
from .utils import logging

def gain_estimation(y,ref,current_gain,max_gain,slices):
    slice_length = len(y)//slices
    amplitude = 0.0
    for i in range(slices):
        start_id = i* slice_length
        end_id = (i + 1) * slice_length if (i + 1) * slice_length <= len(y) else len(y)
        slice = y[start_id:end_id]
        amplitude += np.max(np.abs(slice))
    amplitude /= slices

    #2047 est la valeur maximale sortant de l'adc
    #mais il y a normalisation dans gnuradio de -.5 à .5
    if amplitude >= 0.47:       #0.47
        gain = current_gain - 10
        return gain
    elif amplitude < 0.005 and gain >= max_gain - 4:
        gain = current_gain - 20
        return gain

    target_amplitude = ref * 0.5        #0.5

    if amplitude != 0:
        gain = target_amplitude / amplitude
    else:
        gain = 1
    #20.log pour V/V et 10.log pour W/W
    gain = int(20*np.log10(gain))
    gain += current_gain

    if max_gain > 0 and gain > max_gain:    #max gain > 0 ? -> max gain non infini ?
        gain = max_gain
    return gain


class agc(gr.basic_block):
    """
    docstring for block agc_variable
    """

    def __init__(self, ref, max_gain,slices,fsamp,drate,packet_len,gain,callback):
        """
        ref -> valeur target de tension de quantisation
        max_gain -> gain maximum que l'on peut appliquer en rx
        slices -> nombre de morceaux utilisés pour calculer l'amplitude max du signal
        gain -> valeur initiale du gain rx appliqué (par la suite updaté dans agc.py)
        callback -> fonction de callback pour updater la variable
        """
        self.ref = ref
        self.max_gain = max_gain
        self.slices = slices
        self.fsamp = fsamp
        self.drate = drate
        self.osr = int(fsamp/drate)
        self.packet_len = packet_len  # in bytes
        self.gain = gain              #gain appliqué sur le Lime en dB
        self.callback = callback
        self.callback(self.gain)
        self.rem_samples = 0
        #Remaining number of samples in the current paquet

        gr.basic_block.__init__(
            self,
            name="agc",
            in_sig=[np.complex64],
            out_sig=[np.complex64]  # Output will be the same as the input signal
        )

        self.gr_version = gr.version()
        self.logger = logging.getLogger("agc")
        #self.logger.info("init ok")

        # Redefine function based on version
        if LooseVersion(self.gr_version) < LooseVersion("3.9.0"):
            self.forecast = self.forecast_v38
        else:
            self.forecast = self.forecast_v310

    def forecast_v38(self, noutput_items, ninput_items_required):
        """
        input items are samples (with oversampling factor)
        output items are samples (with oversampling factor)
        """
        ninput_items_required[0] = noutput_items

    def forecast_v310(self, noutput_items, ninputs):
        """
        forecast is only called from a general block
        this is the default implementation
        """
        ninput_items_required = [0] * ninputs
        for i in range(ninputs):
            ninput_items_required[i] = noutput_items

        return ninput_items_required

    def general_work(self, input_items, output_items):
        """
        if self.rem_samples > 0:
            N = len(output_items[0])
            n_out = min(self.rem_samples, N)
            output_items[0][:n_out] = input_items[0][:n_out]
            self.consume_each(n_out)
            self.rem_samples -= n_out
            return n_out
        else:
            N = len(output_items[0])
            y = input_items[0][:N]
            self.gain = gain_estimation(y,self.ref,self.gain,self.max_gain,self.slices)
            self.callback(self.gain)
            output_items[0][:N] = input_items[0][:N]
            self.consume_each(N)
            return N

        """
        N = len(output_items[0])
        #we process maximum one packet at a time
        #input_bytes = input_items[0][:self.packet_len + 1]
        #self.consume_each(self.packet_len+1)
        input_bytes = input_items[0]
        #reprend le signal composant le paquet
        self.logger.info("------> Current gain: %d",self.gain)
        y = input_bytes
        self.logger.info("------> Some values: %s",np.abs(y[0:10]))
        self.gain = gain_estimation(y,self.ref,self.gain,self.max_gain,self.slices)
        self.logger.info("------> New gain: %d",self.gain)
        self.callback(self.gain)
        #the block is transparent, i.e., all input goes to output
        output_items[0][:N] = input_items[0][:N]
        self.consume_each(N)
        return N