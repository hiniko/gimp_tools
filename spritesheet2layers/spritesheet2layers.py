#!/usr/bin/env python2

# Spritesheets2layers.py
# Sherman Rose 2020
#
# This utility is for processing and "Fixing up" sprite sheets of animations to play better in Unity
# A single layer sprite sheet is cut in to cells, with one cell per layer. This allows you to adjust the boundries
# or position of the sprites.
# In my case it was necessary when dealing with animated cells, to have an expected cell size and to reposition both vertically
# and horizontally in order to get a consistant animation
#
# Usage:
# The user is expected to have defined guides that define a rectangle around the extremities of the sprites. Ignore alpha pixels
# or the backgound colour if you use one. There can be empty cells.
#
# When the script is run, it will ask you for the following:
# - Cell Width: Width in px you want the resulting 'cell' of the sprite to be
# - Cell Height: Height in px you want the resulting 'cell' of the sprite to be
# - Cells Per Row: How many cells should be in a row
# - Skip Even Cells: If you are dealing with a sheet that does not already have contiguous cells, and has evenly spaced gaps enable this option
#     assuming that your first intersection of guides defines the first sprite, each area afterwards should empty as well as the next row.
#     This assumption is much faster and easier then checking every pixel.
# - Bottom Offset: Use this for automatic vertical alignment. This is the amount in px from the bottom the sprite should be. If
#      0, it the cell with be vertically centered
# - New Guides: If enabled the scipt clears old guides and then creates a new set of gudides based on Cell Width and Cell Height
# - New Sub Guides: If enabled with new Guides it will create more guides that are half of cell width and cell height. This is useful for
#     further manual alignment 
#
# Any issues or quesitons please email sherman@shermarnose.uk
# Made with thanks to Peter Brooks, Karn Bianco(layers2spritesheet.py), Manish Singh for the guide code (py-slice.py)
#
# Example Run:
#
# See:
# An Example run
# https://imgur.com/a/oqUkk7J
#   
# Manish Singh's py-slice.py included in GIMP (great code to get lists of guides!)
#
# Karn Bianco's layers2spritehseet.py for being the inspiration / learning resource
# http://karnbianco.co.uk/blog/2018/04/10/tutorial-animated-spritesheets-with-gimp-and-unity/
# 
# License - CC0  https://creativecommons.org/publicdomain/zero/1.0/ 



from gimpfu import *
import math
import sys 
import gtk
import array

def spritesheet2layers(image, cell_x_px, cell_y_px, cells_per_row, skip_even_cells, offset_bottom, new_guides, new_sub_guides):
  # Uncomment for debugging
  #sys.stderr = open('C:/temp/python-fu-spritesheet2layers.txt','a')
  #sys.stdout= sys.stderr # So that they both go to the same file

  #print("--- Starting spritesheets2layers.py")

  img = image
  pdb.gimp_image_undo_group_start(img)

  # Get a list of guides  
  vGuides, hGuides = get_guides(img)
  #print("Horizontal:" + str(len(hGuides)))
  #print("Vertical:" + str(len(vGuides)))

  if (not len(vGuides) or not len(hGuides)):
    message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
    message.set_markup("No Guides defined, Found " + str(len(vGuides)) + " vertical, " + str(len(hGuides)) + " horizontal")
    message.run()
    #print("No guides!")

  pdb.gimp_selection_none(img)

  base_layer = image.active_layer
  base_width = base_layer.width
  base_height = base_layer.height

  # Cut out all of the cells in the guide honouring skip_event cells if needed
  for j in range(0, len(hGuides) -1):

    if skip_even_cells:
      if j%2 > 0: continue

    for i in range(0, len(vGuides) -1):

      if skip_even_cells:
        if i%2 > 0: continue

      x1 = img.get_guide_position(vGuides[i])
      y1 = img.get_guide_position(hGuides[j])

      x2 = img.get_guide_position(vGuides[i+1])
      y2 = img.get_guide_position(hGuides[j+1])

      startX = x1
      startY = y1
      width = x2-x1
      height = y2-y1

      #print(x1, y1, x2, y2, width, height)

      pdb.gimp_selection_none(img)
      pdb.gimp_image_select_rectangle(img, CHANNEL_OP_REPLACE, startX, startY, width, height)
      sel = pdb.gimp_image_get_selection(img)

      pdb.gimp_edit_copy(base_layer)

      fsel = pdb.gimp_edit_paste(img.active_layer, False)
      pdb.gimp_floating_sel_to_layer(fsel)
      pdb.gimp_image_lower_layer_to_bottom(img, img.active_layer)
      pdb.plug_in_autocrop_layer(img, img.active_layer)

  img.remove_layer(base_layer)

  # Move all of the layers to the new cell position, centering in the middle but also accounting fo bottom_offset for custom alignment
  for (idx,l) in enumerate(image.layers):
    orig_offsets = l.offsets
    l.name = "Cell " + str(idx)

    x_offset = ((idx % cells_per_row) * cell_x_px) + ((cell_x_px - l.width ) / 2)
    y_offset = round((idx / cells_per_row) * cell_y_px) + ((cell_y_px - l.height) / 2)

    if offset_bottom > 0:
      y_offset = round((idx / cells_per_row) * cell_y_px) + (cell_x_px - offset_bottom - l.height)

    pdb.gimp_layer_set_offsets(l, x_offset, y_offset)
    #print(idx, l.name, orig_offsets, " -> ", l.offsets)

  layer_count = len(img.layers)

  image_width = cell_x_px * cells_per_row
  image_height = round(cell_y_px * ((round(layer_count, -1) + cells_per_row) / cells_per_row ))

  if skip_even_cells:
    image_height = image_height - cell_y_px

  pdb.gimp_image_resize(img, image_width, image_height, 0,0)

  # Make new guides with sub guides if neededkj
  if new_guides:
    pdb.script_fu_guides_remove(img, img.active_layer)
    vert_guides = int(img.width / cell_x_px) +1
    hoz_guides = int(img.height / cell_y_px) +1

    for x in range(0, vert_guides):
      pdb.gimp_image_add_vguide(img, x * cell_x_px)

      if(new_sub_guides):
        sub = x * cell_x_px + int(cell_x_px / 2)
        if sub < img.width:
          pdb.gimp_image_add_vguide(img, sub)

    for y in range(0, hoz_guides):
      pdb.gimp_image_add_hguide(img, y * cell_y_px)

      if(new_sub_guides):
        sub = y * cell_y_px + int(cell_y_px / 2)
        if sub < img.height:
          pdb.gimp_image_add_hguide(img, sub)

  #print("Done") 
  pdb.gimp_image_undo_group_end(img)

class GuideIter:
    def __init__(self, image):
        self.image = image
        self.guide = 0

    def __iter__(self):
        return iter(self.next_guide, 0)

    def next_guide(self):
        self.guide = self.image.find_next_guide(self.guide)
        return self.guide

def get_guides(image):
    vguides = []
    hguides = []

    for guide in GuideIter(image):
        orientation = image.get_guide_orientation(guide)

        guide_position = image.get_guide_position(guide)

        if guide_position >= 0:
            if orientation == ORIENTATION_VERTICAL:
                if guide_position <= image.width:
                    vguides.append((guide_position, guide))
            elif orientation == ORIENTATION_HORIZONTAL:
                if guide_position <= image.height:
                    hguides.append((guide_position, guide))

    def position_sort(x, y):
        return cmp(x[0], y[0])

    vguides.sort(position_sort)
    hguides.sort(position_sort)

    vguides = [g[1] for g in vguides]
    hguides = [g[1] for g in hguides]

    return vguides, hguides
# Register the plugin with Gimp so it appears in the filters menu
register(
    "python-fu-spritesheet2layers",
    "Takes a sprite sheet and cuts to layers based on the guides",
    "Takes a sprite sheet and cuts to layers based on the guides",
    "Sherman Rose",
    "Sherman Rose",
    "2020",
    "SpriteSheet 2 Layers",
    "*",
    [
        (PF_IMAGE, 'image', 'Input image:', None),
        (PF_INT8, "cell_x_px", "Cell Size X",  150),
        (PF_INT8, "cell_y_px", "Cell Size Y",  150),
        (PF_INT8, "cells_per_row", "Cells Per Row", 10),
        (PF_BOOL, "skip_even_cells", "Skip Even Cells", False),
        (PF_INT8, "bottom_offset", "Offset from bottom", 0),
        (PF_BOOL, "new_guides", "Make new guides", True),
        (PF_BOOL, "new_sub_guides", "Make new sub guides", True)

    ],
    [],
    spritesheet2layers, menu="<Image>/Shamwham/")

main()