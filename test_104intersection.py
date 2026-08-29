"""
Automated test suite for the 104Intersection CLI script.

Invokes the script as a subprocess (it has no .py extension, so the
interpreter is passed explicitly) and asserts on stdout / exit code.
"""

import subprocess
import sys
import os
import pytest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "104intersection")


def run(*args):
    return subprocess.run(
        [sys.executable, SCRIPT, *args],
        capture_output=True,
        text=True,
    )


# ---------------------------------------------------------------------------
# Happy path (documented README examples)
# ---------------------------------------------------------------------------

def test_readme_sphere_example():
    result = run("1", "0", "0", "0", "1", "0", "0", "1")
    assert result.returncode == 0
    expected = (
        "sphere of radius 1\n"
        "straight line going through the (0,0,0) point and of direction vector (1,0,0)\n"
        "2 intersection points :\n"
        "(-1.000, 0.000, 0.000)\n"
        "(1.000, 0.000, 0.000)\n"
    )
    assert result.stdout == expected


def test_readme_cylinder_example():
    result = run("2", "0", "0", "0", "0", "0", "1", "1")
    assert result.returncode == 0
    expected = (
        "cylinder of radius 1\n"
        "straight line going through the (0,0,0) point and of direction vector (0,0,1)\n"
        "No intersection point.\n"
    )
    assert result.stdout == expected


def test_cone_tangent_through_apex():
    result = run("3", "0", "0", "0", "0", "0", "1", "45")
    assert result.returncode == 0
    assert "cone of 45 degree angle" in result.stdout
    assert "1 intersection point :" in result.stdout
    assert "(0.000, 0.000, 0.000)" in result.stdout


# ---------------------------------------------------------------------------
# Edge cases: boundary / zero / degenerate values
# ---------------------------------------------------------------------------

def test_sphere_tangent_line_one_point():
    # Line x=1, direction (0,1,0), sphere radius 1 -> tangent at (1,0,0)
    result = run("1", "1", "0", "0", "0", "1", "0", "1")
    assert result.returncode == 0
    assert "1 intersection point :" in result.stdout
    assert "(1.000, 0.000, 0.000)" in result.stdout


def test_sphere_zero_direction_vector_exits_84():
    # a == 0 (zero direction vector) is an explicitly guarded degenerate case
    result = run("1", "0", "0", "0", "0", "0", "0", "1")
    assert result.returncode == 84


def test_cylinder_line_lies_on_surface_infinite_points():
    result = run("2", "1", "0", "0", "0", "0", "1", "1")
    assert result.returncode == 0
    assert "There is an infinite number of intersection points." in result.stdout


def test_zero_radius_sphere():
    # Degenerate sphere of radius 0 (a point at the origin), line through origin
    result = run("1", "0", "0", "0", "1", "0", "0", "0")
    assert result.returncode == 0
    assert "sphere of radius 0" in result.stdout


# ---------------------------------------------------------------------------
# Bad input: should fail gracefully (exit 84), never an unhandled traceback
# ---------------------------------------------------------------------------

def test_missing_args_exits_84():
    result = run("1", "0", "0")
    assert result.returncode == 84
    assert result.stderr == ""


def test_no_args_exits_84():
    result = run()
    assert result.returncode == 84
    assert result.stderr == ""


def test_invalid_opt_exits_84():
    result = run("9", "0", "0", "0", "1", "0", "0", "1")
    assert result.returncode == 84
    assert result.stderr == ""


def test_non_integer_args_exit_84():
    result = run("1", "0", "0", "0", "1.5", "0", "0", "1")
    assert result.returncode == 84
    assert result.stderr == ""


# ---------------------------------------------------------------------------
# Known issue: floating-point equality checks in the cone branch
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    reason=(
        "Known issue: the cone (opt=3) branch derives a/b/c from math.tan(), so an "
        "exactly-degenerate configuration (line lying on the cone surface) essentially "
        "never satisfies the code's exact `a == 0` / `b == 0` / `c == 0` float comparisons "
        "(e.g. tan(radians(45)) != 1.0 exactly). Instead of reporting 'infinite number of "
        "intersection points', it falls through to the generic quadratic-formula path with "
        "a near-zero `a`, producing a numerically unstable, nonsensical coordinate."
    ),
    strict=False,
)
def test_cone_line_on_surface_reports_infinite_points():
    # Line through (1,0,1) with direction (1,0,1) lies exactly on a 45-degree cone.
    result = run("3", "1", "0", "1", "1", "0", "1", "45")
    assert result.returncode == 0
    assert "There is an infinite number of intersection points." in result.stdout
