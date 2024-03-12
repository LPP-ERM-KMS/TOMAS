.TL
Nuclear instrumentation:
Exercise 2
.AU 
Arthur Adriaens
.AI
Ghent University
.EQ
delim $$
.EN
.NH
Random Numbers
.LT
.SH
Truly Random?
.LT
.PP
I'll be using the Mersenne Twister pseudorandom number
generator, a general test to see if this is in fact a
good random number generator is plotting the next number to
the previous number and see if there's a pattern or not:
.PDFPIC TestRandom.pdf 3i
As there doesn't seem to be a pattern we"ll continue on with this number generator.
.SH
Random direction
.LT
.PP
If we wish to compensate against the clustering at the poles we
would get if we took a unifor $theta$ distribution, we'll
have to take a non-uniform distribution, scaling with
sin($theta$). We'll be using inverse Transform Sampling which
is a method that allows us to sample a general probability
distribution using a uniform random number. After some mathematics we find that, say we have random number $u$ between 0 and 1,
we find $theta$ distributed correctly with:
.EQ
theta = arccos(1-2u)
.EN
.PDFPIC DirectionSphere.pdf 3i
In the above figure it is clear that this gives the right
distribution.
.SH
Random Origin
.LT
.PP
As with the random direction, we can't just uniformly take r to
be between 0 and 40mm and theta uniformly between 0 and 2$pi$.
We'll be using the following algorithm:
.PP
Generate $v sub 1$ uniformly between -1 and +1 and $v sub 2$
between 0 and 1. Calculate $r sup 2 = v sub 1 sup 2 + v sub 2
sup 2$, if $r sup 2 > 1$, start over. Otherwise, the sine ($S$) and cosine (C) of a random angle are given by:
.EQ
S = 2 {{v sub 1} {v sub 2}} / {r sup 2}
.EN
.EQ
C = (v sub 1
sup 2 - v sub 2 )/{r sup 2}
.EN
And the radius is given by r*40 (in millimeters), this gives the following:
.PDFPIC OriginCircle.pdf 3i
.NH
How to solve this problem
.LT
.PP
We've now generated the origin coordinate and the direction,
the way we're going to check whether the particle arrives on
the detector is by first proportionally scaling the direction
vector. I.e if z is 0.6 we check the factor with which we'll
have to scale z to get to 70 (mm) and scale both x and y
with this same factor. We then add on the offset due to the
origin and convert x and y into circular coordinates to check
if the radius is smaller than 60mm. We'll only do this for
directions with z positive as the particles going the opposite
way can never reach the detector.
.NH
What is the solid angle? (a)
.LT
.PP
The solid angle of the detector is given by $4 pi N sub {hit} /
N sub {tot}$, 5 quick simulations of $10 sup 6$ particles each give the following values: 
.EQ
N sub {hit} = 109888,109215,109062,109533,110262
.EN
Corresponding to a solid angle of about 1.377 $+-$ 0.006 steradians. 
.NH
Check to find point source (b)
.LT
.PP
Taking the start position to always be (0,0,0) we find, after 5
calculations of $10 sup 6$ points, a solid angle of 1.511 $+-$
0.0018 steradians. Let's now analytically calculate the
solid angle:
.PP
Of the encapsulating sphere the detector blocks a certain
$theta$:
.EQ
tan( theta ) = 60 over 70 ->
theta = tan sup {-1}  60 over 70 = 0.7086
.EN
So the solid angle is:
.EQ
Omega = int int sub S sin( theta ) d theta d phi = int sub 0
sup 0.7086 sin ( theta ) int sub 0 sup {2 pi} d phi
= 1.5126
.EN
Which is perfectly in line with our estimate.
.NH
Partially covered detector (c)
.LT
.PP
We have the detector covered with a foil except for an opening
in the middle in the shape of a square with a diagonal of 75%
the diameter of the detector. I.e a sidelength of 63.64mm.
This can be added to the program by checking if the
particle falls within this square or not. Doing this
gives:
.EQ
Omega = 0.591 +- 0.004
.EN
.NH
Typical amount of particles (d)
.LT
.PP
as mentioned before, $10 sup 6$ particles is chosen. Looking
back at the previous answers, 5 of these generally gives an
accuracy of about 0.5%. This thus means that $5*10 sup 6$ is a
good number of particles.
.NH
Efficiency (e)
.LT
.PP
The efficiency of the simulation was improved by recognizing 
the fact that no particles with a z direction smaller than
0.1 were going to end up on the detector. So not only
the ones going the opposite way, but also the ones
going almost completely to a combination of the x and y
axes were skipped and set to "missed". This limitation could
be further improved upon by manually calculating the angles
with which the detector would or wouldn't be reached but
as the program ran good enough this wasn't tested119923.
