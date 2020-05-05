#!/usr/bin/python

'''
Takes a tsv file in format sampleID\tlatitude\tlongitude\n" and 
returns an output with with Longhurst codes and the description of
the Longhurst Province where the coordinate is located. It works by parsing a file that
contains lat/long coordinates that bound each province and performing the Crossings Test
on each province.  The Crossings Test is used in computer graphics to quickly
determine if a point is within or outside a polygon by "drawing" a line east from the
input coordinate and seeing how many crossings the line makes with the polygon border.
If there is an odd number of crossings, the point is within the polygon, otherwise the
point is outside the polygon.

Command: python coord2longhurst_batch.py 2longhurst.tsv longhurst_codes.tsv

Original script from:
@ Sara Collins.  MIT.  3/18/2015

Modified 30/04/2020 by @ Shane Hogle UTU/MIT
for python3 compatibility and to operate in 
batch mode
'''

import csv
import sys
from xml.dom.minidom import *

### Get lat and lon from tab delimited file
###--------------------------------------------------------------------------

myinput = str(sys.argv[1])
myoutput = str(sys.argv[2])

with open(myinput) as tsvin:
	tsvreader = csv.reader(tsvin, delimiter="\t", quotechar='"')
	with open(myoutput, 'w') as tsvout:
		tsvwriter = csv.writer(tsvout, delimiter="\t", quotechar='"')
		for row in tsvreader:
			mysamp = str(row[0])
			myLat = float(row[1])
			myLon = float(row[2])

			### Parse GML data from longhurst.xml
			provinces = {}
			tree = parse('longhurst.xml')

			for node in tree.getElementsByTagName('MarineRegions:longhurst'):
				# Get province code, name and bounding box from file
				provCode = node.getElementsByTagName('MarineRegions:provcode')[0].firstChild.data
				provName = node.getElementsByTagName('MarineRegions:provdescr')[0].firstChild.data
				fid = node.getAttribute("fid")
				b = node.getElementsByTagName('gml:coordinates')[0].firstChild.data

				# Parse bounding box coordinates
				b = b.split(' ')
				x1,y1 = b[0].split(',')
				x2,y2 = b[1].split(',')
				x1 = float(x1)
				y1 = float(y1)
				x2 = float(x2)
				y2 = float(y2)

				provinces[fid] = {'provName': provName, 'provCode': provCode, 'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}

			### Find which candidate provinces our coordinates come from.
			inProvince = {}
			for p in provinces:
				inLat = 0
				inLon = 0

				if (myLat>=provinces[p]['y1'] and myLat<=provinces[p]['y2']):
					inLat = 1

				if (myLon>=provinces[p]['x1'] and myLon<=provinces[p]['x2']):
					inLon = 1

				if inLat and inLon:
					inProvince[p] = True


			### Perform Crossings Test on each candidate province.
			for node in tree.getElementsByTagName('MarineRegions:longhurst'):
				fid = node.getAttribute("fid")

				if inProvince.get(fid):
					crossings = 0

					## Get all coordinate pairs for this province.
					geom = node.getElementsByTagName('MarineRegions:the_geom')

					for g in geom:
						c = g.getElementsByTagName('gml:coordinates')

						for i in c:
							ii = i.childNodes
							coordStr = ii[0].data		#<--- contains coordinate strings
							P = coordStr.split(' ')

							pairs = []
							for p in P:
								[lon,lat] = p.split(',')
								pairs.append([float(lon),float(lat)])

							## Use pair p and p+1 to perform Crossings Test.
							for i in range(len(pairs)-1):
								# test latitude
								passLat = (pairs[i][1]>=myLat and pairs[i+1][1]<=myLat) or (pairs[i][1]<=myLat and pairs[i+1][1]>=myLat)

								# test longitude
								passLon = (myLon <= pairs[i+1][0])

								if passLon and passLat:
									crossings += 1

					if crossings%2==1:
						inProvince[fid] = True
					else:
						inProvince[fid] = False

			### Write solution
			solution = []
			for i in inProvince:
				if inProvince[i] == True:
					solution.append([provinces[i]['provCode'], provinces[i]['provName']])

			if len(solution)==0:
				tsvwriter.writerow([mysamp, myLat, myLon, "NA", "Coordinates may be on land"])

			if len(solution) == 1:
				tsvwriter.writerow([mysamp, myLat, myLon, solution[0][0], solution[0][1]])

			if len(solution) > 1:
				tsvwriter.writerow([mysamp, myLat, myLon, "NA", "Multiple Solutions found"])
