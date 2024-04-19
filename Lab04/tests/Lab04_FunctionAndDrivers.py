# 
import os
import sys
from pathlib import Path

import cocotb
from cocotb.runner import get_runner
from cocotb.triggers import Timer
from cocotb.clock import Clock

# cocotb decorator indicating a test to run with simulator.
# multiple tests may be included in the same python module (file)
@cocotb.test()
async def my_test(dut):
    pass



def simulation_runner():
    """Simulate the adder example using the Python runner.

    This file can be run directly or via pytest discovery.
    """
    simulator_program = "ghdl"
    WaveformOptionVcd = "--vcd=Lab02_waveforms.vcd"

    proj_path = Path(__file__).resolve().parent.parent

    vhdl_sources = []
    vhdl_sources += [proj_path / "hdl" / "sqrt_conv.vhd"]

    # equivalent to setting the PYTHONPATH environment variable
    sys.path.append(str(proj_path / "tests"))

    runner = get_runner(simulator_program)
	
    runner.build(
        vhdl_sources=vhdl_sources,
        hdl_toplevel="square_root",
        always=True,
    )
	
    runner.test(hdl_toplevel="square_root", 
				test_module="Lab04_FunctionAndDrivers",
				plusargs=[WaveformOptionVcd, "--ieee-asserts=disable"])


if __name__ == "__main__":
    simulation_runner()
