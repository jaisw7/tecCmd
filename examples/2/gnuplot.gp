set terminal postscript color
set out 'gnuplot.ps'
set xrange [0:3.14]
set yrange [-1:1]
plot 'data.txt' u 1:(sin(pi*$1)) w l
set out
