# 104Intersection

A command-line tool that computes the intersection point(s) of a 3D line with a quadric
surface centered on the origin — a sphere, a cylinder (axis along z), or a double cone (apex
at the origin, axis along z) — given a point on the line and its direction vector.

Note: despite the Epitech-style numbered name, this exercise is implemented in **Python 3**,
not C. There is no Makefile, `src/`, `include/`, or `tests/` directory, so `make` /
`mingw32-make` does not apply here.

## Build

Nothing to compile — it's a Python script.

- **Windows**: `python 104intersection <args>`
- **Unix/macOS/WSL**: `chmod +x 104intersection && ./104intersection <args>`

## Usage

```
python 104intersection opt xp yp zp xv yv zv p
```
- `opt`: `1` = sphere, `2` = cylinder, `3` = cone (anything else exits with code 84)
- `xp yp zp`: a point on the line
- `xv yv zv`: the line's direction vector
- `p`: radius (sphere/cylinder) or half-angle in degrees (cone)

All 8 arguments must parse as integers, or the program exits with code 84.

**Example — sphere (line through the center):**
```
$ python 104intersection 1 0 0 0 1 0 0 1
sphere of radius 1
straight line going through the (0,0,0) point and of direction vector (1,0,0)
2 intersection points :
(-1.000, 0.000, 0.000)
(1.000, 0.000, 0.000)
```

**Example — cylinder (line runs along the axis, entirely inside):**
```
$ python 104intersection 2 0 0 0 0 0 1 1
cylinder of radius 1
straight line going through the (0,0,0) point and of direction vector (0,0,1)
No intersection point.
```

## How it works

The line is parameterized as `P + t*V`. Substituting it into the surface's implicit equation
gives a quadratic `a*t^2 + b*t + c = 0`:
- sphere: `x^2 + y^2 + z^2 = p^2`
- cylinder: `x^2 + y^2 = p^2`
- cone: `x^2 + y^2 = (z * tan(p))^2`, with `p` converted to radians first

`main()` (the module-level code) computes `a`, `b`, `c` for the selected surface, then solves
via the discriminant `delta = b^2 - 4ac`: `delta < 0` → no intersection, `delta == 0` → one
tangent point, `delta > 0` → two points, computed from the two roots and sorted by parameter
`t` before printing. Degenerate cases where `a == 0` (line parallel to the surface's axis) are
handled separately — for the cylinder this reports either "No intersection point" or "infinite
number of intersection points" depending on whether the line lies on the surface; for the cone,
the `a == 0` branch additionally falls back to a linear (one-root) solution when `b != 0`.
