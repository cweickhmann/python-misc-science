#!/usr/bin/python
# -*- coding: utf8 -*-

"""Usage: %(scriptName)s <.msh-file> [-c <int> <colour tag or name> [,-c <int> <tag> [, ...]]] [-o <output TiKZ file>]

%(scriptName)s loads a .msh (gmsh) 2D file and creates a TiKZ 2D plot of the mesh.
The output file name is chosen by default as the same as the input with the suffix
replaced by ".tikz". Colours can be assigned to physical tags by adding the "-c" option.
"""

import argparse
import re
import os

regexes = {"meshformat": "\\$MeshFormat\\n(.*?)\\n\\$EndMeshFormat",
           "nodes": "\\$Nodes\\n(.*?)\\n\\$EndNodes",
           "elements": "\\$Elements\\n(.*?)\\n\\$EndElements",
           "physicalNames": "\\$PhysicalNames\\n(.*?)\\n\\$EndPhysicalNames"
          }


colourdict = {0: "black", 1: "red", 2: "blue", 3: "green", 4: "orange", 5: "blue", 6: "red", 7: "magenta"}

def find_nodes(filestring, base_multiplier):
    nodeslist = []
    m = re.findall(regexes["nodes"], filestring, re.DOTALL)
    if len(m) > 0:
        lines = m[0].split("\n")
        nb = int(lines[0]) # Checking for consistency
        for l in lines[1:]:
            data = l.split(" ")
            data = [float(d)*base_multiplier for d in data]
            nodeslist.append( tuple( data )[1:] ) # drop point number, it's redundant
        # if len(nodeslist) == nb:
        #     print("Points: Yup, that seems to have worked out right...")
    (x, y, z) = tuple( map( list, zip(*nodeslist) ) )
    BoundingBox = tuple( [ (min(el), max(el)) for el in (x,y,z) ] )
    return (nodeslist, BoundingBox)

def find_edges(filestring, nodeslist=None):
    edgeslist = []
    m = re.findall(regexes["elements"], filestring, re.DOTALL)
    if nodeslist == None:
        print("Check disabled...")
    if len(m) > 0:
        lines = m[0].split("\n")
        nb = int(lines[0]) # Checking for consistency
        for l in lines[1:]:
            data = l.split(" ")
            data = [int(d) for d in data]
            el_type = data[1]
            colour = data[3] # if el_type == 1 else 0
            points = tuple( [ d-1 for d in data[-(1+el_type):] ] )
            nodes = xrange(0, len(nodeslist))
            if nodeslist != None and not all( [ p in nodes for p in points ] ):
                raise Exception("One of the nodes of edge %d do not exist (nodes: %d, %d)! Terminating." % (data[0], start, end) )
                return
            edgeslist.append( (colour, ) + points ) # phyiscal tag (el. 3 in data), then points
        # if len(edgeslist) == nb:
        #     print("Edges: Yup, that seems to have worked out right...")
    return edgeslist

"""
def normalise(point, BoundingBox, TargetBound, Axis):
    
    d_bb = [ b[1]-b[0] for b in BoundingBox[Axis] ]
    d_tb = [ b[1]-b[0] for b in TargetBounds ]
    m = float(d_bb)/float(d_tb)
    d_x = [ b[0]*M for (b, M) in zip(BoundingBox, m) ]
    
    return [ p/dx for (p, dx) in zip(point, d_x) ]
"""

def convertFile(fh, outfile=None, base_multiplier=1e3, boundary_colours=None, mesh_colours=None):
    if outfile == None:
        outfile = ".".join( (os.path.split(fh.name)[1]).split(".")[:-1] + ["tikz"] )
    
    boundary_colours = colourdict if boundary_colours is None else boundary_colours
    boundary_colours[0] = "black" if not 0 in boundary_colours.keys() else boundary_colours[0]
    
    mesh_colours = colourdict if mesh_colours is None else mesh_colours
    mesh_colours[0] = "black" if not 0 in mesh_colours.keys() else mesh_colours[0]
    
    filestring = fh.read()
    (nodes, BoundingBox) = find_nodes(filestring, base_multiplier)
    edges = find_edges(filestring, nodes)
    
    with open(outfile, "w+") as fh:
        fh.write("""% \\resizebox{<width or !>}{<height or !>}{\%
        \\begin{tikzpicture}[x=100mm,y=100mm,line join=round,line cap=round]
        """)
        for e in reversed(edges):
            if len(e[1:]) > 2:
                lineopts = ",line width=.05pt"
                colour = mesh_colours[e[0]]
            else:
                lineopts = ",line width=.5pt"
                colour = boundary_colours[e[0]]
            point_str = " -- ".join( [ "(%f,%f)" % ps for ps in tuple([nodes[pt][:-1] for pt in e[1:] ]) ] )
            fh.write("\t\\draw[%s] %s -- cycle;\n" % ( colour+lineopts, point_str ) )
        fh.write("""\\end{tikzpicture}
    % }
    """)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=argparse.FileType('r'), nargs="+", help=".msh-file to convert")
    parser.add_argument("-o", "--outfile", type=argparse.FileType('w+'), help="output filename (defaults to input filename with .tkiz suffix). Warning: File will be overwritten!")
    parser.add_argument("-b", "--base-multiplier", type=float, default=1, help="base multiplier of the drawing (e.g. 1000 or 1e-3)")
    parser.add_argument("-cb", "--boundary-colours", action="append", nargs=2, metavar=('number', 'TeX-name'), help="dict of boundary colours")
    parser.add_argument("-cm", "--mesh-colours", action="append", nargs=2, metavar=('number', 'TeX-name'), help="dict of mesh colours")
    args = parser.parse_args()
    boundary_colours = dict([ [int(k), v] for [k, v] in args.boundary_colours ]) if args.boundary_colours != None else None
    mesh_colours = dict([ [int(k), v] for [k, v] in args.mesh_colours ]) if args.mesh_colours != None else None
    for fn in args.filename:
        convertFile(fn,
                args.outfile,
                base_multiplier=args.base_multiplier,
                boundary_colours=boundary_colours,
                mesh_colours=mesh_colours)

if __name__ == "__main__":
    main()

