set terminal postscript color enhanced size 4.75,4 
set out 'gnuplot.ps'
set datafile separator ","
set logscale y
set format y "10^{%T}"
set border 3 
set xtics nomirror 
set ytics nomirror 
set xtics font 'Helvetica,9' offset 0,+.5
set ytics font 'Helvetica,9' offset .5,0
set xlabel font 'Helvetica-Bold,11' offset 0,+1.2
set ylabel font 'Helvetica-Bold,11' offset 2.2,0
set mxtics
set xlabel 'Non-dimensional time: t/t_0'
set ylabel 'Residual: |f^{n+1} - f^{n}|/|f^{n}|'
set key at 85,85
set yrange [1e-9:1e-3]
set xrange [0:6]
set xtics 0,1,6
plot "<grep 'dgfsresidualstd' data.txt | cut -d ':' -f2-" u 1:2 w l lc 'red' lw 1.5
set out