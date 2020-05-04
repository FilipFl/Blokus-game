import pygame
import random
import numpy as np
from shapes import get_shapes
import time

class Game():
    width = 20
    height = 20
    margin = 1
    window_width = 416
    window_height = 416
    WINDOW_SIZE = [window_width, window_height]

    def __init__(self):
        self.main_board = np.zeros((14, 14))
        self.bufer_board = np.zeros((14, 14))
        self.drawed_board = np.zeros((14, 14))
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(self.WINDOW_SIZE)
        self.done = False
        self.players = []
        p1 = Player(1)
        p2 = Player(2)
        self.players.append(p1)
        self.players.append(p2)
        self.which_playing = 0
        self.key_actions = {
            'LEFT': lambda: self.players[self.which_playing].get_block().move_x(-1, self.main_board),
            'RIGHT': lambda:    self.players[self.which_playing].get_block().move_x(1, self.main_board),
            'DOWN': lambda: self.players[self.which_playing].get_block().move_y(1, self.main_board),
            'UP': lambda:   self.players[self.which_playing].get_block().move_y(-1, self.main_board),
            'r': lambda:    self.players[self.which_playing].get_block().rotate(self.main_board),
            'f': lambda:    self.players[self.which_playing].get_block().flip(self.main_board),
            'n': lambda:    self.players[self.which_playing].previous(),
            'm': lambda:    self.players[self.which_playing].next(),
            'SPACE': lambda:    self.place_block()
        }

    def text_objects(self, text, font,color):
        textSurface = font.render(text, True, color)
        return textSurface, textSurface.get_rect()

    def message_display(self, msg, x, y, w, h):
        smallText = pygame.font.Font("freesansbold.ttf", 12)
        textSurf, textRect = self.text_objects(msg, smallText, (255, 255, 255))
        textRect.center = ((x + (w / 2)), (y + (h / 2)))
        self.screen.blit(textSurf, textRect)

    def big_message_display(self, text):
        largeText = pygame.font.Font('freesansbold.ttf', 50)
        TextSurf, TextRect = self.text_objects(text, largeText,(255,255,255))
        TextRect.center = ((self.window_width / 2), (self.window_height/ 2))
        self.screen.blit(TextSurf, TextRect)


    def button(self, msg, x, y, w, h, ic, ac, action=None):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if x + w > mouse[0] > x and y + h > mouse[1] > y:
            pygame.draw.rect(self.screen, ac, (x, y, w, h))
            if click[0] == 1 and action is not None:
                action()
                time.sleep(1)
        else:
            pygame.draw.rect(self.screen, ic, (x, y, w, h))
        smallText = pygame.font.Font("freesansbold.ttf", 10)
        textSurf, textRect = self.text_objects(msg, smallText,(0,0,0))
        textRect.center = ((x + (w / 2)), (y + (h / 2)))
        self.screen.blit(textSurf, textRect)


    def draw_everything(self):
        self.button("Brak ruchów",25,370,70,30,(140,0,0),(220,0,0),self.players[self.which_playing].cant_play)
        self.message_display("Czerwony: "+str(np.count_nonzero(self.main_board==1)),150,2,100,30)
        self.message_display("Niebieski: " + str(np.count_nonzero(self.main_board == 2)), 150, 19, 100, 30)
        for row in range(14):
            for column in range(14):
                color = (255,255,255)
                if self.bufer_board[row][column] != 0 or self.main_board[row][column] != 0:
                    if self.bufer_board[row][column] == 7:
                        if self.players[self.which_playing].get_block().check_collision(self.main_board) == -1:
                            color = (200, 200, 200)
                        elif self.which_playing == 0:
                            color = (250, 0, 0)
                        elif self.which_playing == 1:
                            color = (0,0,250)
                    elif self.main_board[row][column] == 1:
                        color = (180,0,0)
                    elif self.main_board[row][column] == 2:
                        color = (0, 0, 180)
                pygame.draw.rect(self.screen,
                                 color,
                                 [(self.margin + self.width) * column + self.margin + 50,
                                  (self.margin + self.height) * row + self.margin + 50,
                                  self.width,
                                  self.height])
                if ((row == 3 and column ==3) or (row ==10 and column == 10)) and (self.bufer_board[row][column] == 0
                                        and self.main_board[row][column] == 0 and self.drawed_board[row][column]==0):
                    pygame.draw.circle(self.screen,(0,0,0),(int((self.margin + self.width) * column + self.margin + 50 +(self.width/2)),
                                  int((self.margin + self.height) * row + self.margin + 50+(self.height/2))), 5,1)
        self.clock.tick(60)
        pygame.display.flip()
        if self.players[0].unable_to_play() and self.players[1].unable_to_play():
            self.endgame()

    def main_game(self):
        if self.players[self.which_playing].unable_to_play():
            self.give_turn()
        self.bufer_board = np.where(self.main_board != 0, self.main_board, self.bufer_board)
        self.bufer_board = np.where(self.bufer_board == 7, 0, self.bufer_board)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
            elif event.type == pygame.KEYDOWN:
                for key in self.key_actions:
                    if event.key == eval("pygame.K_"
                                         + key):
                        self.key_actions[key]()
        self.screen.fill((0, 0, 0))
        block = self.players[self.which_playing].get_block()
        self.bufer_board[block.get_y():block.get_y() + block.get_shape().shape[0],
        block.get_x():block.get_x() + block.shape_brick.shape[1]] = block.get_shape()
        self.drawed_board = np.zeros((14, 14))
        self.drawed_board[block.get_y():block.get_y() + block.get_shape().shape[0],
        block.get_x():block.get_x() + block.shape_brick.shape[1]] = block.get_shape()
        self.draw_everything()



    def is_done(self):
        return self.done

    def close(self):
        if self.done:
            pygame.quit()

    def place_block(self):
        if self.players[self.which_playing].get_block().check_collision(self.main_board) != -1:
            self.main_board = np.where(self.drawed_board == 7, self.which_playing+1, self.main_board)
            self.players[self.which_playing].place_block()
            if self.which_playing == 0:
                self.which_playing = 1
            else:
                self.which_playing = 0

    def give_turn(self):
        if self.which_playing == 0:
            self.which_playing = 1
        else:
            self.which_playing = 0
        self.players[self.which_playing].get_block().set_position(6, 6)

    def endgame(self):
        self.screen.fill((0, 0, 0))
        self.done = True
        if np.count_nonzero(self.main_board==1)<np.count_nonzero(self.main_board==2):
            self.big_message_display("Wygrał Niebieski!")
        elif  np.count_nonzero(self.main_board==1)>np.count_nonzero(self.main_board==2):
            self.big_message_display("Wygrał Czerwony!")
        else:
            self.big_message_display("Remis!")
        pygame.display.flip()
        time.sleep(5)
        self.close()

class Player():
    def __init__(self, number):
        self.blocks_stack = []
        for i in range(0, 20):
            b = (Block(i))
            self.blocks_stack.append(b)
        self.points = 0
        self.chosen_block = len(self.blocks_stack)-1
        self.which = number
        self.is_out_of_moves = False

    def place_block(self):
        self.blocks_stack.pop(self.chosen_block)
        self.chosen_block = len(self.blocks_stack)-1

    def next(self):
        self.chosen_block += 1
        if self.chosen_block == len(self.blocks_stack):
            self.chosen_block = 0
        self.blocks_stack[self.chosen_block].set_position(6, 6)

    def previous(self):
        self.chosen_block -= 1
        if self.chosen_block == -1:
            self.chosen_block = len(self.blocks_stack)-1
        self.blocks_stack[self.chosen_block].set_position(6, 6)

    def get_block(self):
        return self.blocks_stack[self.chosen_block]

    def unable_to_play(self):
        return self.is_out_of_moves

    def cant_play(self):
        self.is_out_of_moves = True



class Block():
    def __init__(self, number):
        self.shape_brick = np.array(get_shapes(number))
        self.x_position = 6
        self.y_position = 6
        self.shape_brick = np.where(self.shape_brick == -1,  7, self.shape_brick)
        self.is_on_something = False

    def check_collision(self, board):
        for y, row in enumerate(self.shape_brick):
            for x, cell in enumerate(row):
                try:
                    if cell and board[y + self.y_position, x + self.x_position]:
                        self.is_on_something = True
                        return -1
                    if self.x_position+self.shape_brick.shape[1] > 14 or self.y_position+self.shape_brick.shape[0] > 14:
                        return 1
                    if self.x_position < 0 or self.y_position < 0:
                        return 1
                except IndexError:
                    return 1
        return 0

    def rotate(self, board):
        board = np.where(board == 1, 0, board)
        old = self.shape_brick
        self.shape_brick = np.rot90(self.shape_brick)
        if self.check_collision(board) == 1:
            self.shape_brick = old
        elif self.check_collision(board) == -1:
            self.is_on_something = True

    def flip(self, board):
        board = np.where(board == 1, 0, board)
        old = self.shape_brick
        self.shape_brick = np.transpose(self.shape_brick)
        self.rotate(board)
        if self.check_collision(board) == 1:
            self.shape_brick = old
        elif self.check_collision(board) == -1:
            self.is_on_something = True

    def move_x(self, movement, board):
        board = np.where(board == 1, 0, board)
        old_x = self.x_position
        self.x_position += movement
        if self.check_collision(board) == 1:
            self.x_position = old_x
        elif self.check_collision(board) == -1:
            self.is_on_something = True

    def move_y(self, movement, board):
        board = np.where(board == 1, 0, board)
        old_y = self.y_position
        self.y_position += movement
        if self.check_collision(board) == 1:
            self.y_position = old_y
        elif self.check_collision(board) == -1:
            self.is_on_something = True

    def set_position(self, x, y):
        self.x_position = x
        self.y_position = y

    def get_x(self):
        return self.x_position

    def get_y(self):
        return self.y_position

    def get_shape(self):
        return self.shape_brick


if __name__ == '__main__':
    game = Game()
    while not game.is_done():
        game.main_game()
    game.close()

