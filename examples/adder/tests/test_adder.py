# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0
# Simple tests for an adder module
import os
import random
import sys
from pathlib import Path
from sys import argv

import cocotb
from cocotb.runner import get_runner
from cocotb.triggers import Timer

if cocotb.simulator.is_running():
    from adder_model import adder_model


@cocotb.test()
async def adder_basic_test(dut):
    """Test for 5 + 10"""

    A = 5
    B = 10

    dut.A.value = A
    dut.B.value = B

    await Timer(2, units="ns")

    assert dut.X.value == adder_model(
        A, B
    ), f"Adder result is incorrect: {dut.X.value} != 15"


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


def test_adder_runner():
    """Simulate the adder example using the Python runner.

    This file can be run directly or via pytest discovery.
    """

    style = 'text'
    if len(argv) > 1:
        style = argv[1]
    assert style in ('text', 'gui', 'vis')

    hdl_toplevel_lang = os.getenv("HDL_TOPLEVEL_LANG", "verilog")
    sim = os.getenv("SIM", "questa")

    proj_path = Path(__file__).resolve().parent.parent
    # equivalent to setting the PYTHONPATH environment variable
    sys.path.append(str(proj_path / "model"))

    verilog_sources = []
    vhdl_sources = []

    if hdl_toplevel_lang == "verilog":
        verilog_sources = [proj_path / "hdl" / "adder.sv"]
    else:
        vhdl_sources = [proj_path / "hdl" / "adder.vhdl"]

    build_test_args = []
    if hdl_toplevel_lang == "vhdl" and sim == "xcelium":
        build_test_args = ["-v93"]

    # equivalent to setting the PYTHONPATH environment variable
    sys.path.append(str(proj_path / "tests"))

    runner = get_runner(sim)
    runner.build(
        verilog_sources=verilog_sources,
        vhdl_sources=vhdl_sources,
        hdl_toplevel="adder",
        always=True,
        build_args=build_test_args,
    )

    test_args = list(build_test_args)
    if style == 'vis':
        test_args.extend(('-visualizer', '-qwavedb=+signal+memory+vhdlvariable'))

    runner.test(
        hdl_toplevel="adder", test_module="test_adder", test_args=test_args, gui=(style != 'text')
    )


if __name__ == "__main__":
    test_adder_runner()
