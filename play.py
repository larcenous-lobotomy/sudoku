#Randomly generate puzzle for user
import pygame, sys
from pygame.locals import *
from funcs import *
import time

class Cell :
    #height and width of cell in px is fixed at 60*60    
    height = 60
    width = 60
    
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.selected = False
        self.changeable = True
        self.val = 0
    
    #dual purpose - setting values and highlighting border if selected  
    def draw(self, win) :        
        fnt = pygame.font.SysFont("comicsans", 40)

        gap = 60
        x = self.col * gap
        y = self.row * gap

        if not self.changeable: 
            pygame.draw.rect(win, (128,128,128), (x,y,gap,gap), 0) 
            
        if self.changeable :
            pygame.draw.rect(win, (255,255,255), (x,y,gap,gap), 0) 
        
        if  self.val != 0:
            text = fnt.render(str(self.val), 1, (0, 0, 0))
            win.blit(text, (x + 15, y + 5))
            
class Grid :
    def __init__(self, level): 
        #dimensions of grid in pixels
        self.width = 540
        self.height = 540
        self.cell_list = [[Cell(i,j) for j in range(9)] for i in range(9)]
        self.vals = [[0 for j in range(9)] for i in range(9)]
        #contains a tuple of row, col of selected cell
        self.selected = None
        #puzzle is a list of two matrices -
        #A random solved matrix
        #An unsolved matrix generated from above matrix (with proper difficulty level)        
        self.puzzle = random_grid(level)
        for row in range(9) :
            for col in range(9) :
                self.cell_list[row][col].val = self.puzzle[1][row][col]
                self.vals[row][col] = self.puzzle[1][row][col]
                if not self.cell_list[row][col].val == 0 :
                    #preset values are unselectable and unchangeable
                    self.cell_list[row][col].changeable = False         
    
    #redraws table and its contents    
    def draw(self, win):
        #draw cells
        for i in range(9) :
            for j in range(9) :
                self.cell_list[i][j].draw(win)
        # Draw Grid Lines
        gap = self.width / 9
        for i in range(10):
            if i % 3 == 0 and i != 0:
                thick = 4
            else:
                thick = 1
            pygame.draw.line(win, (0,0,0), (0, i*gap), (self.width, i*gap), thick)
            pygame.draw.line(win, (0,0,0), (i*gap, 0), (i*gap, self.height), thick)
        for i in range(9) :
            for j in range(9) :
                if self.cell_list[i][j].selected :
                    pygame.draw.rect(win, (255,0,0), (j*60,i*60,60,60), 3)
                    
    
    #making a selection (and deselecting others) - selects only changeable cells        
    def selection(self,row, col) :
        flag = False
        if self.cell_list[row][col].selected :
            flag = True
        for i in range(9) :
            for j in range(9) :
                self.cell_list[i][j].selected = False
        if self.cell_list[row][col].changeable and not flag:
            self.cell_list[row][col].selected = True
            self.selected = row, col
        else :
            self.selected = None
    
    #to determine selected cell, given position of cursor  (not generalised for the rest of the board)  
    def click_loc(self, pos) :
        if pos[0] < self.width and pos[1] < self.height :
            return pos[1] // 60, pos[0] // 60   
        else : 
            return None
        
#check whether board is filled and is worthy of being checked !
#return value - NONE (if incompletely filled), TRUE(if correctly filled), FALSE(if incorrectly filled)
def check(board) :   
    for i in range(9) :
        for j in range(9) :
            if board.cell_list[i][j].val == 0 :
                return None
    #sudoku matrix 
    for i in range(9) :
        for j in range(9) :
            if  not valid(board.vals, board.vals[i][j], (i, j)) :
                return False
    return True

#return formatted time
def format_time(secs):
    sec = secs%60
    minute = secs//60
    hour = minute//60
    hour = str(hour + 100)[-2:]
    minute = str(minute + 100)[-2:]
    sec = str(sec + 100)[-2:]

    timer = hour + ":" + minute + ":" + sec
    return timer

#Play function callable in main        
def PLAY(win) :
    img = pygame.image.load("left_arrow.png")
    re = pygame.image.load("undo.png")
    while True :
        #clear window contents
        win.fill((255,255,255))
        #drawing the buttons for level setting
        term_x = [200, 400]
        term_y = [200, 250, 300, 350]
        gamerun = False
        level = None  
        key = None
        run = True
        while run :
            #redraw options table    
            for i in range(4) :
                pygame.draw.line(win, (128, 128, 128), (term_x[0], term_y[i]), (term_x[1], term_y[i]))
            for i in range(2) :
                pygame.draw.line(win, (128, 128, 128), (term_x[i], 200), (term_x[i], 350))
            fnt = pygame.font.SysFont("comicsans", 40)    
            options = ["EASY", "MEDIUM", "HARD"]
            text = [fnt.render(options[i], 0, (128, 128, 128)) for i in range(3)]
            x = [200, 400]
            y = [200, 250, 300,350]
            for i in range(3) :
                win.blit(text[i], (220, y[i] - 5))  
            win.blit(img, (0, 550))
            pygame.display.update()
                
            for event in pygame.event.get() :
                #if quit detected
                if event.type == QUIT :
                    pygame.quit()
                    sys.exit()
                                        
                #detecting the mouseclick and checking which button was selected (and breaking out from 2 loops)
                elif event.type == MOUSEBUTTONDOWN :
                    x, y = pygame.mouse.get_pos()
                    if x > 200 and x < 400 and y > 200:
                        if y < 250 :
                            level = 0
                            run = False
                            break
                        elif y < 300 :
                            level = 1
                            run = False
                            break
                        elif y < 350 :
                            level = 2
                            run = False
                            break
                    elif x > 0 and x < 50 and y > 560 and y < 600:
                        return

        gamerun = True
        #clear window contents to construct Sudoku grid
        win.fill((255,255,255))
        board = Grid(level)
        exit = False
        start = time.time()
        timer = 0
        #print solution in terminal in readable format to make evaluation easier
        for row in board.puzzle[0] :
            print(row)
        print()
        print()
        while gamerun :
            if not exit :
                board.draw(win)
                pygame.draw.rect(win, (150,150,150), (0, 544, 300, 60))
                style = pygame.font.SysFont("comicsans", 40)
                win.blit(style.render("EVALUATE", 1, (0, 0, 0)), (80,540))
                win.blit(img, (0, 550))
                pygame.draw.line(win, (0,0,0), (60,540), (60,600), 4)
                pygame.draw.rect(win,(255,255,255), (300,550,300,80),0)
                pygame.draw.line(win, (0,0,0), (300,540), (300,600), 4)
                pygame.draw.line(win, (0,0,0), (360,540), (360,600), 4)
                timer = int(time.time() - start)
                lstyle = pygame.font.SysFont("comicsans", 40)
                win.blit(lstyle.render(format_time(timer), 1, (0,0,0)), (370, 540))
                if board.selected != None :
                    if valid(board.vals, board.vals[board.selected[0]][board.selected[1]], board.selected) == False:
                        win.blit(lstyle.render("X", 1, (255,0,0)), (320, 540))
                    elif valid(board.vals, board.vals[board.selected[0]][board.selected[1]], board.selected) == True:
                        win.blit(lstyle.render("V", 1, (0,255,0)), (320, 540))
                pygame.display.update()
            for event in pygame.event.get() :
                #if quit is detected
                if event.type == QUIT :
                    pygame.quit()
                    sys.exit()
                    
                #if user clicks on screen
                elif event.type == MOUSEBUTTONDOWN and not exit:
                    x, y = pygame.mouse.get_pos()
                    #if user clicks somewhere on the grid
                    if not board.click_loc((x,y)) == None :
                        row, col =  board.click_loc((x,y))
                        board.selection(row, col)
                    #if user clicks on "Check", evaluate only if user has completely filled the table
                    elif x > 60 and x < 300 and y > 540 and y < 600: 
                        result = check(board)
                        fnt = pygame.font.SysFont("comicsans", 50)
                        if result :
                            text = "CORRECT in %s" % (format_time(timer))
                            color = (0,255,0)
                        elif not result :
                            text = "WRONG ANSWER"
                            color = (255,0,0)
                        if type(result) == bool :
                            win.fill((255,255,255))
                            txt = fnt.render(text, True, color)
                            win.blit(txt, (40, 300))
                            win.blit(re, (200, 400))
                            pygame.display.update()
                            while True :
                                for event in pygame.event.get() :
                                    if event.type == QUIT :
                                        pygame.quit()
                                        sys.exit()
                                    elif event.type == MOUSEBUTTONDOWN :
                                        x, y = pygame.mouse.get_pos()
                                        if x > 200 and x < 264 and y > 400 and y < 464 :
                                            return
                    #user clicks on back
                    elif x > 0 and x < 50 and y > 560 and y < 600:
                        gamerun = False 
                        run = True

                #if user presses a key                     
                elif event.type == KEYDOWN and not exit:
                    if event.key == pygame.K_1:
                        key = 1
                    elif event.key == pygame.K_2:
                        key = 2
                    elif event.key == pygame.K_3:
                        key = 3
                    elif event.key == pygame.K_4:
                        key = 4
                    elif event.key == pygame.K_5:
                        key = 5
                    elif event.key == pygame.K_6:
                        key = 6
                    elif event.key == pygame.K_7:
                        key = 7
                    elif event.key == pygame.K_8:
                        key = 8
                    elif event.key == pygame.K_9:
                        key = 9
                    #offers delete feature    
                    elif event.key in [pygame.K_DELETE, pygame.K_BACKSPACE] : 
                        key = 0
                    #if some box has been selected prior to hitting key
                    if board.selected != None :
                        if board.cell_list[board.selected[0]][board.selected[1]].changeable:
                            board.cell_list[row][col].val = key
                            board.vals[row][col] = key
                            board.draw(win)   
                
                pygame.display.update()
             
                
    
    
