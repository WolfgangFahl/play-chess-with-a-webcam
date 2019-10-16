import sys
from collections import defaultdict

COLUMN_LETTER = {0:'A', 1:'B', 2:'C', 3:'D', 4:'E', 5:'F', 6:'G', 7:'H'}
ROW_NUMBER = {0:str(1), 1:str(2), 2:str(3), 3:str(4), 4:str(5), 5:str(6), 6:str(7), 7:str(8)}

REV_COLUMN = {'A':1, 'B':2, 'C':3, 'D':4, 'E':5, 'F':6, 'G':7, 'H':8}
REV_ROW = {'1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8}

def GetCellName(column,row):
    """Returns the cell name string given 0-based column and row"""
    return ''.join([COLUMN_LETTER[column], ROW_NUMBER[row]])
    
def GetColumnFromName(name):
    return REV_COLUMN[name[0]]

def GetRowFromName(name):
    return REV_ROW[name[1]]

def GetCellColor(column, row):
    """Returns the capitalized color name ("WHITE"|"BLACK") of a cell according to its adress. 
       Notice that pair adresses (e.g. col=3 row=1 : C1) are black"""
    options = {0:"BLACK", 1:"WHITE"}
    return options[(row+column)%2]
    
def GetDominator(name, dominatorOffset):
    coff = dominatorOffset[0]
    roff = dominatorOffset[1]
    col = GetColumnFromName(name)
    row = GetRowFromName(name)
    if(col+coff > 8 or col+coff < 1 or row+roff > 8 or row+roff < 1) :
        return None
    return GetCellName(col+coff-1, row+roff-1)
    
def GetDominated(name, dominatorOffset):
    return GetDominator(name, (-1*dominatorOffset[0],-1*dominatorOffset[1]))
    
def SplitDomination(cells, dominatorOffset):
    """If a cell's dominator is in cells too, the cell is dominated and the dominator is identified.
        If a cell's dominator is not in cells, then cell is a dominator"""
    dominator = []
    dominated = []
    for cell in cells:
        dominatorCell = GetDominator(cell, dominatorOffset)
        dominatedCell = GetDominated(cell, dominatorOffset)
        
        if isInList(dominatorCell,cells):
            dominated.append(cell)
            dominator.append(dominatorCell)
        else:
            dominator.append(cell)
    return dominator, dominated
    
        
def isInList(anItem, aList):
    try:
        aList.index(anItem)
        return True
    except:
        return False
        
def isPossibleMoveWhitePawn(fromCell, toCell):
    fromRow, toRow, fromCol, toCol = _getFromTo(fromCell, toCell)
    if toRow == fromRow +1 and (toCol == fromCol or toCol == fromCol+1 or toCol == fromCol-1):
            return True
    elif toCol == fromCol and toRow == 4 and fromRow == 2:
        return True
    return False
    
def isPossibleMoveBlackPawn(fromCell, toCell):
    fromRow, toRow, fromCol, toCol = _getFromTo(fromCell, toCell)
    if toRow == fromRow -1 and (toCol == fromCol or toCol == fromCol+1 or toCol == fromCol-1):
            return True
    elif toCol == fromCol and toRow == 5 and fromRow == 7:
        return True
    return False
    
def isPossibleMoveRook(fromCell, toCell):
    fromRow, toRow, fromCol, toCol = _getFromTo(fromCell, toCell)
    return(fromRow == toRow) or (fromCol == toCol)
    
def isPossibleMoveBishop(fromCell, toCell):
    fromRow, toRow, fromCol, toCol = _getFromTo(fromCell, toCell)
    return abs(fromRow - toRow) == abs(fromCol - toCol)   
    
def isPossibleMoveQueen(fromCell, toCell):
    return isPossibleMoveRook(fromCell, toCell) or isPossibleMoveBishop(fromCell, toCell)
    
def isPossibleMoveKing(fromCell, toCell):
    """Does not consider the castle move"""
    fromRow, toRow, fromCol, toCol = _getFromTo(fromCell, toCell)
    return abs(toRow-fromRow) <= 1 and abs(toCol-fromCol) <= 1
    
def isPossibleMoveKnight(fromCell, toCell):
    fromRow, toRow, fromCol, toCol = _getFromTo(fromCell, toCell)
    return (abs(toRow-fromRow) == 2 and abs(toCol-fromCol) == 1) or (abs(toRow-fromRow) == 1 and abs(toCol-fromCol) == 2)
    
def _getFromTo(fromCell, toCell):
    fromRow = GetRowFromName(fromCell)
    toRow = GetRowFromName(toCell)
    fromCol = GetColumnFromName(fromCell)
    toCol = GetColumnFromName(toCell)
    return fromRow,toRow,fromCol,toCol
    
if __name__ == "__main__":
    sys.stderr.write("Not a stand alone")