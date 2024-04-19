# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0
# modified from the cocotb main repository, v1.8.1
#    cocotb\examples\matrix_multiplier\tests

import math
import os
import sys
from pathlib import Path
from random import getrandbits
from typing import Any, Dict, List

import cocotb
from cocotb.binary import BinaryValue
from cocotb.clock import Clock
from cocotb.handle import SimHandleBase
from cocotb.queue import Queue
from cocotb.runner import get_runner
from cocotb.triggers import RisingEdge
from cocotb.log import SimLog



# reused from the cocotb repo, unmodified. Added some inline comments
class DataValidMonitor:
    """
    Reusable Monitor of one-way control flow (data/valid) streaming data interface

    Args
        clk: clock signal
        valid: control signal noting a transaction occured
        datas: named handles to be sampled when transaction occurs
    """

    def __init__(
        self, clk: SimHandleBase, datas: Dict[str, SimHandleBase], valid: SimHandleBase
    ):
        # Queue object, manages values sampled when valid == 1
        # Using a python dictionary is not required here, but
        # remains a more flexible approach for more complex modules.
        #     See example in main cocotb git repository for
        #     example with multiple sample values using this dictionary approach 
        #     cocotb\examples\matrix_multiplier\tests
        self.values = Queue[Dict[str, int]]()
        # dut clock
        self._clk = clk
        # link to signals containing data, passed to the constructor. 
        #            For lab 6, only one value is kept
        #            the cocotb original example recorded multiple signals 
        #            using a python dictionary
        self._datas = datas
        # Valid/enable signal
        self._valid = valid
        # member/pointer, indicating if the coroutine is running
        self._coro = None

    def start(self) -> None:
        """Start monitor"""
        if self._coro is not None:
            raise RuntimeError("Monitor already started")
        # schedule start of the monitoring thread
        self._coro = cocotb.start_soon(self._run())

    def stop(self) -> None:
        """Stop monitor"""
        if self._coro is None:
            raise RuntimeError("Monitor never started")
        
        # stop monitoring thread.
        self._coro.kill()
        self._coro = None

    async def _run(self) -> None:
        # infinite loop
        while True:
            # wait for next rising edge of clock
            await RisingEdge(self._clk)
            
            # if the valid/enable bit  is not '1'
            # wait until it becomes '1' and skip to 
            # next clock cycle
            if self._valid.value.binstr != "1":
                await RisingEdge(self._valid)
                continue
            
            # Valid/enable was '1'. Store data in the queue.
            self.values.put_nowait(self._sample())

    def _sample(self) -> Dict[str, Any]:
        """
        Samples the data signals and builds a transaction object

        Return value is what is stored in queue. Meant to be overriden by the user.
        """
        # but this works for the simple "enable == 1" case. So
        # no modifications for the RT2024 workshop
        return {name: handle.value for name, handle in self._datas.items()}


class MMC_sqrt:
    """
    Reusable checker of a matrix_multiplier instance

    Args
        matrix_multiplier_entity: handle to an instance of matrix_multiplier
    """

    # instead of the dut (top level), here the constructor expects
    # the instance for the hdl module, as labeled in the VHDL file.
    # this will be done in the base class, and passed as an argument
    # to the constructor through inst_Sqrt.
    def __init__(self, inst_Sqrt):
        self.inst_Sqrt = inst_Sqrt
        self.log = SimLog("cocotb.base.%s" % (type(self).__qualname__))

        self.input_mon = DataValidMonitor(
            clk=self.inst_Sqrt.clk,
# change the "fill with" parts below
            valid=self.inst_Sqrt.arg_valid,
            datas=dict(Argument=self.inst_Sqrt.arg),
        )

        self.output_mon = DataValidMonitor(
            clk=self.inst_Sqrt.clk, 
# change the "fill with" parts below
            valid=self.inst_Sqrt.sqrt_valid, 
            datas=dict(SqrtResult=self.inst_Sqrt.sqrt_res)
        )

        self._checker = None

    def start(self) -> None:
        """Starts monitors, model, and checker coroutine"""
        if self._checker is not None:
            raise RuntimeError("Monitor already started")
        self.input_mon.start()
        self.output_mon.start()
        self._checker = cocotb.start_soon(self._check())

    def stop(self) -> None:
        """Stops everything"""
        if self._checker is None:
            raise RuntimeError("Monitor never started")
        self.input_mon.stop()
        self.output_mon.stop()
        self._checker.kill()
        self._checker = None

    def model(self, model_input_value: int) -> int:
        # to fill. Calculate the integer square root from the
        # model_input_value. You can use the library of your
        # choice (math module, numpy, etc)
        # Make sure the final value is an integer
        Expected = math.sqrt(model_input_value)
        Expected = math.floor(Expected)
        
        self.log.info("Model predicts: " + str(Expected))
        return Expected

    async def _check(self) -> None:
        while True:
            actual = await self.output_mon.values.get()
            expected_inputs = await self.input_mon.values.get()
            expected = self.model(
                model_input_value=expected_inputs["Argument"]
            )
            assert actual["SqrtResult"] == expected

