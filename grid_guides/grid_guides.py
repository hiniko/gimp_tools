#!/usr/bin/env python2

# gridguides.py
# Sherman Rose 2020 sherman@shermarnose.uk
# Make a grid of guides takes in x and y for spaces between vertical and horizontal guides

from gimpfu import *

def python_fu_grid_guides(img, x, y, clear_prev):

  if clear_prev:
    pdb.script_fu_guides_remove(img, img.active_layer)
  
  for v in range(0, int(img.width / x) + 1):
    pdb.gimp_image_add_vguide(img, x * v)

  for h in range(0, int(img.height / y) + 1):
    pdb.gimp_image_add_hguide(img, y * h)
 
register(
    "python-fu-grid-guides",
    "Make a guid of guides",
    "Takes a sprite sheet and cuts to layers based on the guides",
    "Sherman Rose",
    "Sherman Rose",
    "2020",
    "Grid Guides",
    "*",
    [
        (PF_IMAGE, 'image', 'Input image:', None),
        (PF_INT8, "x", "X Spacing",  150),
        (PF_INT8, "y", "Y Space",  150),
        (PF_BOOL, "clear_prev", "Clear Previous", True)
    ],
    [],
    python_fu_grid_guides, menu="<Image>/Shamwham/")

main()