#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Board import Board
from Field import Field, FieldROI
          

def test_PixelListGenerators():
    board=Board()
    field=Field(board,0,0)
    field.width=100
    field.height=100
    field.pcx=50
    field.pcy=50
    field.step=7
    field.distance=3
    assert list(FieldROI.split(field.step))==[0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875]
    roi=FieldROI(field,FieldROI.split(field.step),FieldROI.split(field.step))
    assert list(roi.pixelList())==[(13, 13), (13, 25), (13, 38), (13, 50), (13, 63), (13, 75), (13, 88), (25, 13), (25, 25), (25, 38), (25, 50), (25, 63), (25, 75), (25, 88), (38, 13), (38, 25), (38, 38), (38, 50), (38, 63), (38, 75), (38, 88), (50, 13), (50, 25), (50, 38), (50, 50), (50, 63), (50, 75), (50, 88), (63, 13), (63, 25), (63, 38), (63, 50), (63, 63), (63, 75), (63, 88), (75, 13), (75, 25), (75, 38), (75, 50), (75, 63), (75, 75), (75, 88), (88, 13), (88, 25), (88, 38), (88, 50), (88, 63), (88, 75), (88, 88)]

   
    
test_PixelListGenerators()