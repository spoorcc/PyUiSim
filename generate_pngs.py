"""
Basic example that shows how to generate png from svg and use it in tkinter
"""

import os
from copy import deepcopy
from svg import Parser, Rasterizer, SVG
from PIL import Image, ImageTk
import xml.etree.ElementTree as ET

import logging
logging.basicConfig(level=logging.DEBUG)

SVG_ELEMENTS = ['path', 'rect', 'circle', 'ellipse', 'line', 'polygon', 'polyline', 'text']
SVG_ELEMENTS_XPATH = ['.//' + el_type for el_type in SVG_ELEMENTS]

def create_png_from_svg(svg, png_name):
    svg = Parser.parse_file(svg)
    logging.info('Image is {} by {}.'.format(svg.width, svg.height))
    
    rast = Rasterizer()
    buff = rast.rasterize(svg, svg.width, svg.height)
    
    im = Image.frombytes('RGBA', (svg.width, svg.height), buff)
    im.save(png_name)

def create_png_from_svg_string(svg, png_name):
    svg = Parser.parse(svg)
    logging.info('Image is {} by {}.'.format(svg.width, svg.height))
    
    rast = Rasterizer()
    buff = rast.rasterize(svg, svg.width, svg.height)
    
    im = Image.frombytes('RGBA', (svg.width, svg.height), buff)
    im.save(png_name)

def read_namespace_free_xml(xml):
    ''' SVG have a namespace, just strip it to make the rest of the code more trivial '''
    it = ET.iterparse(xml)
    for _, el in it:
        if '}' in el.tag:
            el.tag = el.tag.split('}', 1)[1]  # strip all namespaces
        for at in el.attrib.keys(): # strip namespaces of attributes too
            if '}' in at:
                newat = at.split('}', 1)[1]
                el.attrib[newat] = el.attrib[at]
                del el.attrib[at]
    return it.root

def create_svg_with_graphical_elements_hidden(svg):
    ''' pynanosvg doesn't yet pick-up the visibility attribute, use display none to hide elements '''
    with open(svg, 'r') as opened_file:
        root = read_namespace_free_xml(opened_file)

        for element_type in SVG_ELEMENTS_XPATH:
            for path in root.iterfind(element_type):
                path.set('display','none')

    return ET.ElementTree(root)

def render_png_for_each_svg_element(root, format_string):
    ''' Turning each element on, one-by-one and render a png '''

    counter = 0
    for element_type in SVG_ELEMENTS_XPATH:
        for elt in root.iterfind(element_type):
            file_path = format_string.format(counter)

            elt.set('display','')
            create_png_from_svg_string(ET.tostring(root.getroot()),
                                       file_path + '.png')
            elt.set('display','none')
            counter += 1

OUTDIR = 'images/output'

try:
    os.mkdir(OUTDIR)
    svg = create_svg_with_graphical_elements_hidden('images/bcd_digit.svg')
    render_png_for_each_svg_element(svg, os.path.join(OUTDIR, 'bcd_digit{}'))
except FileExistsError:
    pass
