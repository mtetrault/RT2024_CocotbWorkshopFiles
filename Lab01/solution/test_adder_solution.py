# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0
# Simple tests for an adder module
import os
import random
import sys
from pathlib import Path

import cocotb
from cocotb.runner import get_runner
from cocotb.triggers import Timer

if cocotb.simulator.is_running():
    from adder_model import adder_model


@cocotb.test()
async def adder_randomised_test(dut):
    """Test for adding 2 random numbers multiple times"""

    for i in range(10):

        A = random.randint(0, 15)
        B = random.randint(0, 15)

        dut.A.value = A
        dut.B.value = B

        await Timer(2, units="ns")

        assert dut.X.value == adder_model(
            A, B
        ), "Randomised test failed with: {A} + {B} = {X}".format(
            A=dut.A.value, B=dut.B.value, X=dut.X.value
        )


def adder_runner():
    """Simulate the adder example using the Python runner.

    This file can be run directly or via pytest discovery.
    """
    hdl_toplevel_lang = os.getenv("HDL_TOPLEVEL_LANG", "vhdl")
    sim = os.getenv("SIM", "ghdl")

    proj_path = Path(__file__).resolve().parent.parent
    # equivalent to setting the PYTHONPATH environment variable
    sys.path.append(str(proj_path / "model"))

    verilog_sources = []
    vhdl_sources = []

    if hdl_toplevel_lang == "verilog":
        verilog_sources = [proj_path / "hdl" / "adder.sv"]
    else:
        vhdl_sources = [proj_path / "hdl" / "adder.vhdl"]

    # equivalent to setting the PYTHONPATH environment variable
    sys.path.append(str(proj_path / "tests"))
    
    
    # https://docs.cocotb.org/en/stable/library_reference.html#cocotb.runner.get_runner
    runner = get_runner(sim)

    # https://docs.cocotb.org/en/stable/library_reference.html#cocotb.runner.Simulator.build
    runner.build(
        verilog_sources=verilog_sources,
        vhdl_sources=vhdl_sources,
        hdl_toplevel="adder",
        always=True,
    )

    
    WaveformOptionVcd = "--vcd=Lab01_waveforms.vcd"

    # https://docs.cocotb.org/en/stable/library_reference.html#cocotb.runner.Simulator.test
    #runner.test(hdl_toplevel="adder", test_module="test_adder_solution")
    #runner.test(hdl_toplevel="adder", test_module="test_adder_solution", test_args=WaveformOptionVcd,)
    #runner.test(hdl_toplevel="adder", test_module="test_adder_solution", test_args=[WaveformOptionVcd],)
    runner.test(hdl_toplevel="adder", test_module="test_adder_solution", plusargs=[WaveformOptionVcd])


if __name__ == "__main__":
    adder_runner()
