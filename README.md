# Longhurst-Province-Finder

Takes a tsv file in format sampleID\tlatitude\tlongitude\n" and 
returns an output with with Longhurst codes and the description of
the Longhurst Province where the coordinate is located. It works by parsing a file that
contains lat/long coordinates that bound each province and performing the Crossings Test
on each province.  The Crossings Test is used in computer graphics to quickly
determine if a point is within or outside a polygon by "drawing" a line east from the
input coordinate and seeing how many crossings the line makes with the polygon border.
If there is an odd number of crossings, the point is within the polygon, otherwise the
point is outside the polygon.

Original script from:
@ Sara Collins.  MIT.  3/18/2015
https://github.com/thechisholmlab/Longhurst-Province-Finder

Modified 30/04/2020 by @ Shane Hogle UTU/MIT
for python3 compatibility and to operate in 
batch mode

