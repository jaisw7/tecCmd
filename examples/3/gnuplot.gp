set terminal postscript color
set out 'gnuplot.ps'
set xrange [0:3.14]
set yrange [-1:1]
f(x) = sin(pi*x)
plot f(x) w l
set out
