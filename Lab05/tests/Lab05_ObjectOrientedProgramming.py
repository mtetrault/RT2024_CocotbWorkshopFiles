# 
import os
import random
import sys
import math
from pathlib import Path

import cocotb
from cocotb.runner import get_runner
from cocotb.triggers import Timer
from cocotb.clock import Clock
from cocotbext.uart import UartSource, UartSink
from cocotb.log import SimLog

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
        await self.test()
        await self.postTest()
    
    # put drivers here (UART)
    def BuildEnvironment(self):
        # put the UART driver and sink declarations here as objects
        # self.UARTUnit = UartSource(...) 
        pass
    
    # Initialize dut signals, clock and run the reset sequence
    async def InitSignalsClockAndReset(self):
        pass
        
    # Virtual function, forces to use derived class.
    async def test(self):
        # Mimmick C++ Pure virtual function. 
        raise NotImplementedError()

    # Put anything happening at the end of the simulation here.
    # for the lab, a delay followed by rising the reset.
    async def postTest(self):
        pass
        
    # Wrapper around driver, to send values to the dut.
    async def SendValue(self, ValueToDut):
        pass
    
    # Read back the value and convert to integer.
    async def ReadResult(self):
        # result_BytesArray = await self.???.read(count=1)
        result_BytesArray = 0 ## to replace
        result_bytes = bytes(result_BytesArray)
        result_int = int.from_bytes(result_bytes, "little")
        return result_int


# Define a test-specific sequence.
class EmptyTestClass(BaseEnvironment):
    async def test(self):
        # intentionally empty. Test does nothing.
        Timer(100, units='ns')
        pass
        

# Define another test-specific sequence.
class OtherEmptyTestClass(BaseEnvironment):
    async def test(self):
        # intentionally empty. Test does nothing.
        Timer(400, units='ns')
        pass

# Function(s) that will be called by the simulator.
@cocotb.test()
async def EmptyTest(dut):
    print("Starting empty test")
    runObject = EmptyTestClass(dut)
    await runObject.run()
    

@cocotb.test()
async def OtherEmptyTest(dut):
    print("Starting other empty test")
    runObject = OtherEmptyTestClass(dut)
    await runObject.run()
    
    
    
    
# Runner, same as in previous labs.
def simulation_runner():
    """Simulate the adder example using the Python runner.

    This file can be run directly or via pytest discovery.
    """
    hdl_toplevel_lang = "vhdl"
    simulator_program = "ghdl"
	
    WaveformOptionVcd = "--vcd=Lab05_waveforms.vcd"

    proj_path = Path(__file__).resolve().parent.parent

    vhdl_sources = []
    vhdl_sources += [proj_path / "hdl" / "uart_rx.vhd"]
    vhdl_sources += [proj_path / "hdl" / "uart_tx.vhd"]
    vhdl_sources += [proj_path / "hdl" / "sqrt_conv.vhd"]
    vhdl_sources += [proj_path / "hdl" / "RT2024MySystemTop.vhd"]

    # equivalent to setting the PYTHONPATH environment variable
    sys.path.append(str(proj_path / "tests"))

    runner = get_runner(simulator_program)

    runner.build(
        vhdl_sources=vhdl_sources,
        hdl_toplevel="rt2024mysystemtop",
        always=True,
    )

    runner.test(hdl_toplevel="rt2024mysystemtop", 
        test_module="Lab05_ObjectOrientedProgramming",
        plusargs=[WaveformOptionVcd, "--ieee-asserts=disable"])


if __name__ == "__main__":
    simulation_runner()
