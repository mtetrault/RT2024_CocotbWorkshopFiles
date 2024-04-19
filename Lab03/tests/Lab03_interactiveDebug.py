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
async def sqrt_test(dut):

    test_value = 4
    expected_result = 2

    c = Clock(dut.clk, 100, 'ns')
    await cocotb.start(c.start())

    dut.reset.value = 1
    await cocotb.triggers.ClockCycles(dut.clk, 5, rising=True)
    dut.reset.value = 0
    await cocotb.triggers.ClockCycles(dut.clk, 2, rising=True)

    dut.arg.value = test_value
    dut.arg_valid.value = 1
    await cocotb.triggers.ClockCycles(dut.clk, 1, rising=True)
    dut.arg_valid.value = 0

    while(dut.sqrt_valid.value == 0):
        await cocotb.triggers.ClockCycles(dut.clk, 1, rising=True)

    assert dut.sqrt_res.value == expected_result

    # for adding some extra cycles in gtkwave
    # wait for 10 clock
    await cocotb.triggers.ClockCycles(dut.clk, 10, rising=True)
    dut.reset.value = 1
    await cocotb.triggers.ClockCycles(dut.clk, 3, rising=True)



def simulation_runner():
    """Simulate the adder example using the Python runner.

    This file can be run directly or via pytest discovery.
    """
    hdl_toplevel_lang = "vhdl"
    simulator_program = "ghdl"
	
    WaveformOptionVcd = "--vcd=Lab02_waveforms.vcd"

    proj_path = Path(__file__).resolve().parent.parent

    vhdl_sources = []
    vhdl_sources += [proj_path / "hdl" / "sqrt_conv.vhd"]

    # equivalent to setting the PYTHONPATH environment variable
    sys.path.append(str(proj_path / "test_solution"))

    runner = get_runner(simulator_program)
	
    runner.build(
        vhdl_sources=vhdl_sources,
        hdl_toplevel="square_root",
        always=True,
    )
	
    runner.test(hdl_toplevel="square_root", 
				test_module="Lab03_interactiveDebug",
				plusargs=[WaveformOptionVcd, "--ieee-asserts=disable"])


if __name__ == "__main__":
    simulation_runner()
