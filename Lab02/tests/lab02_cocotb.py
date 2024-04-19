# 
import os
import sys
from pathlib import Path

import cocotb
from cocotb.runner import get_runner
from cocotb.triggers import Timer

# Define your test here. See first lab or CodeSnippets.py 
# for decorator and other special Python kewords
def mytest():
    # https://docs.cocotb.org/en/stable/triggers.html#cocotb.triggers.Timer
    # Do nothing for 100 ns
    # note there is a missing keyword before "Timer"
    Timer(100, units='ns')
    pass
    
# Cocotb/GHDL runner. Use the first lab as template.
def simulation_runner():
    """Simulate the adder example using the Python runner.

    This file can be run directly or via pytest discovery.
    """
    hdl_toplevel_lang = "vhdl"
    simulator_program = "ghdl"
    TopModule = "???"

    vhdl_sources = []

    runner = get_runner(simulator_program)
	
    runner.build(
        vhdl_sources=vhdl_sources,
        hdl_toplevel="???",
        always=True,
    )
	
    runner.test(hdl_toplevel="???", 
				test_module="????", # name of this python file.
				plusargs=[])


if __name__ == "__main__":
    simulation_runner()
