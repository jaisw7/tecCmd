# tecCmd
tecCmd is a utility for generating publication quality plots effortlessly. I wrote the script around 2018. I used it extensively during my PhD. 

I was using gnuplot initially for plotting data. Gnuplot is excellent. But the output files are not suitable for directly putting into publications. An another plotting software is Tecplot. It is extensively used in the field of computational fluid dynamics for visualization. Around 2018, Tecplot released a python API for their Tecplot-360. This means that we need not launch a GUI to plot data. The command line utilities are much more memory efficient. They also open up opportunities for automation using simple bash scripting. A Python API together with evil *eval* can be exploited for data manipulation. 

### Examples

See the examples directory for the input data files.

#### Example 1

<table>
<tr>
    <th> gnuplot </th>
    <th> tecCmd </th>
</tr>

<tr>
  <td><pre>

    set terminal postscript
    set out 'gnuplot.ps'
    plot 'data.txt' u 1:2
    set out
    
  </pre></td>
  <td><pre>

    set out 'tecCmd.ps'
    plot 'data.txt' u 1:2
    set out
   
  </pre></td>
</tr>


<tr>
    <td><img src="examples/1/gnuplot.png"></td>
    <td><img src="examples/1/tecCmd.png"></td>
</tr>


</table>
