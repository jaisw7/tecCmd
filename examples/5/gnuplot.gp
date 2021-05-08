set terminal postscript color enhanced
set out 'gnuplot.ps'
set datafile separator ","
set logscale y
set xlabel 'Non-dimensional time: t/t_0'
set ylabel 'Residual: |f^{n+1} - f^{n}|/|f^{n}|'
set key at 85,85
set yrange [1e-9:1e-3]
set xrange [0:6]
set xtics 0,1,6
plot "<grep 'dgfsresidualstd' data.txt | cut -d ':' -f2-" u 1:2 w l lc 'red'
set out