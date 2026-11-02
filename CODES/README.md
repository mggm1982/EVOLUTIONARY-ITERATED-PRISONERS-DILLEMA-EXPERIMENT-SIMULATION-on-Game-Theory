0. To run the codes, matplotplusplus library is required so that the results 
which have been been produced through my cpp codes can be visualised in graphs
this was needed because a viasual representation of how population proportions change
across generations in such a game theory experiment gives us a full picture of that 
particular experiment run very well , which may be difficult to interpret if we were 
to simply have an array of numbers that represented populations across generations 


REQUIREMENT: MSYS UCRT 64 TERMINAL 
command which may be useful if some dependency is missing : 

pacman -S --needed mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-cmake mingw-w64-ucrt-x86_64-ninja mingw-w64-ucrt-x86_64-gnuplot git



1. the folder of codes contains a source folder with the main.cpp file 

2. after downloading the codes folder we navigate to this codes folder using msys ucrt64
terminal. 

if we then run the command: bash build_and_run_ucrt64.sh 
it should install the dependent libraries , build and run the code. 

the exact content of the script: 
{
#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build
./build/EvolutionaryPD.exe }





3. we may test the functionality of the program using this case

any random seed
uniform population 200 each
alpha = 1
error = 0.01
forgiveness = 0.01

note : although the output is completely dependent on the random seed 
we can check if the program is working or not and if the graph plot is being produced

note: as a fallback measure, the population history is also printed after 
ones presses enter to exit if the graph is not visible due to errors in the plotting 
dependency. 



SPECIAL NOTE: As a safety measure against failure of the code completely 
due to the plotting library dependency, i have added a separate fallback source
file which gives the output in the terminal as text and not a graph plot , this 
fallback code will be indepdent of any complicated libraries. 


