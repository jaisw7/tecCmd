set terminal postscript
set out 'gnuplot.ps'
plot 'data.txt' u 1:2
set out
