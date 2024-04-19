# 
import os
import logging
import random
import sys
import math
from pathlib import Path

import debugpy

import cocotb
from cocotb.runner import get_runner
from cocotb.triggers import Timer
from cocotb.clock import Clock
from cocotbext.uart import UartSource, UartSink
from cocotb.log import SimLog

from Lab06_MMC_Sqrt_solution import MMC_sqrt

# Example class. Copy-paste section from the previous labs in the methods
# Add the "self." keyword where appropriate (i.e. : self.dut.Signal).
class BaseEnvironment:
    def __init__(self, dut):
        # keep pointer to dut in class
        self.dut = dut
        self.log = SimLog("cocotb.base.%s" % (type(self).__qualname__))

    # Common sequence for all tests
    async def run(self):
        self.BuildEnvironment()
        await self.InitSignalsClockAndReset()
        self.StartEnvironment()
        await self.test()
        await self.postTest()
    
    # put drivers here (UART)
    def BuildEnvironment(self):
        # put the UART driver and sink declarations here as objects
        # self.UARTUnit = UartSource(...) 
        self.uart_driver = UartSource(self.dut.rx_uart_serial_in, baud=1000000, bits=8)
        self.uart_sink   = UartSink(self.dut.tx_uart_serial_out, baud=1000000, bits=8)
        # task.log.setLevel(logging.DEBUG)
        self.uart_driver.log.setLevel(logging.DEBUG)
        self.inst_MMC_Sqrt = MMC_sqrt(self.dut.inst_square_root)
        
    def StartEnvironment(self):
        self.inst_MMC_Sqrt.start()
    
    # Initialize dut signals, clock and run the reset sequence
    async def InitSignalsClockAndReset(self):
        self.dut.rx_uart_serial_in.value = 1
        self.dut.reset.value = 1
        
        self.c = Clock(self.dut.clk, 100, 'ns')
        await cocotb.start(self.c.start())
        
        ## delay for reset
        await cocotb.triggers.ClockCycles(self.dut.clk, 10, rising=True)
        
        ## release reset
        self.dut.reset.value = 0
        await cocotb.triggers.ClockCycles(self.dut.clk, 2, rising=True)
        
        
    # Virtual function, forces to use derived class.
    async def test(self):
        # Mimmick C++ Pure virtual function. 
        raise NotImplementedError()

    # Put anything happening at the end of the simulation here.
    # for the lab, a delay followed by rising the reset.
    async def postTest(self):
        await cocotb.triggers.ClockCycles(self.dut.clk, 10, rising=True)
        self.dut.reset.value = 1
        await cocotb.triggers.ClockCycles(self.dut.clk, 2, rising=True)
        self.inst_MMC_Sqrt.stop()
        
    # Wrapper around driver, to send values to the dut.
    async def SendValue(self, ValueToDut):
        await self.uart_driver.write(ValueToDut.to_bytes(1, "little"))
        await self.uart_driver.wait()
    
    # Read back the value and convert to integer.
    async def ReadResult(self):
        # result_BytesArray = await self.???.read(count=1)
        result_BytesArray = await self.uart_sink.read(count=1)
        result_bytes = bytes(result_BytesArray)
        result_int = int.from_bytes(result_bytes, "little")
        return result_int


class DirectedTestClass(BaseEnvironment):
    async def test(self):
        TestValues = [4, 9, 16, 50]
        ExpectedValues = [2, 3, 4, 7]
        for Test, Expected in zip(TestValues, ExpectedValues):
        
            await self.SendValue(Test)
            DutResponse = await self.ReadResult()
            assert DutResponse == Expected

class RandomTestClass(BaseEnvironment):
    
    async def test(self):
        for x in range(0, 5):
            
            RandomValue = random.randint(0, 255)
            Expected = math.sqrt(RandomValue)
            Expected = math.floor(Expected)
            
            await self.SendValue(RandomValue)
            DutResponse = await self.ReadResult()
            assert DutResponse == Expected


@cocotb.test()
async def RandomTest(dut):
    runObject = RandomTestClass(dut)
    runObject.log.info("Starting RandomTest")
    await runObject.run()
    
    
@cocotb.test()
async def DirectedTest(dut):

    #debugpy.listen(5678)
    #debugpy.wait_for_client()
    #debugpy.breakpoint()
    runObject = DirectedTestClass(dut)
    runObject.log.info("Starting DirectedTest")
    await runObject.run()
    

    
    
    
    
# Runner, same as in previous labs.
def simulation_runner():
    """Simulate the adder example using the Python runner.

    This file can be run directly or via pytest discovery.
    """
    hdl_toplevel_lang = "vhdl"
    simulator_program = "ghdl"
	
    WaveformOptionVcd = "--vcd=Lab06_waveforms.vcd"

    proj_path = Path(__file__).resolve().parent.parent

    vhdl_sources = []
    vhdl_sources += [proj_path / "hdl" / "uart_rx.vhd"]
    vhdl_sources += [proj_path / "hdl" / "uart_tx.vhd"]
    vhdl_sources += [proj_path / "hdl" / "sqrt_conv.vhd"]
    vhdl_sources += [proj_path / "hdl" / "RT2024MySystemTop.vhd"]

    # equivalent to setting the PYTHONPATH environment variable
    sys.path.append(str(proj_path / "solution"))

    runner = get_runner(simulator_program)

    runner.build(
        vhdl_sources=vhdl_sources,
        hdl_toplevel="rt2024mysystemtop",
        always=True,
    )

    runner.test(hdl_toplevel="rt2024mysystemtop", 
        test_module="Lab06_MainEnvironment_solution",
        plusargs=[WaveformOptionVcd, "--ieee-asserts=disable"])


if __name__ == "__main__":
    simulation_runner()
