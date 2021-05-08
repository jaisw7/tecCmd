set terminal postscript color
set out 'gnuplot.ps'
set xrange [-1:1]
set yrange [-1:1]
P0(x) = 1
P1(x) = x
P2(x) = 0.5*(3*x**2-1)
P3(x) = (35*x**4-30*x**2+3)/8.
P4(x) = (63*x**5-70*x**3+15*x)/8.
plot P0(x) w l lc 'red' t 'P0', \
     P1(x) w l lc 'green' t 'P1', \
     P2(x) w l lc 'blue' t 'P2', \
     P3(x) w l lc 'orange' t 'P3', \
     P4(x) w l lc 'magenta' t 'P4'
set out
