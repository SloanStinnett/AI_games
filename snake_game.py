import pygame as pyg 
import random as rand
from enum import Enum
from collections import namedtuple
from dataclasses import dataclass

pyg.init()

BLOCK_SIZE:int = 20
SPEED:int = 20
SMALL_FONT = pyg.font.Font('MoiraiOne-Regular.ttf',25)
BIG_FONT = pyg.font.Font('MoiraiOne-Regular.ttf',50)

Point = namedtuple('Point','x, y')


WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
BLUE = (0,0,255)
CYAN = (0,100,255)
GREY = (127,127,127)
GREEN = (0,255,0)



class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

class Action(Enum):
    STRAIGHT = 1
    RIGHT = 2
    LEFT = 3

class GameType(Enum):
    HUMAN_PLAYER = 1
    AI_PLAYER = 2
    AI_TRAIN = 3



class SnakeGame:
    ''' class containing the behavior of the snake game'''
    def __init__(self, w:int = 400, h:int = 400):
        '''intializes snake game and display '''
        self.width = w
        self.height = h
        self.display = pyg.display.set_mode((self.width,self.height))
        self.clock = pyg.time.Clock()

        self.reset_gamestate()
    
    def reset_gamestate(self):
        self.direction = Direction.UP
        self.head = Point(self.width/2,self.height/2)
        self.snake = [self.head,
                      Point(self.head.x-BLOCK_SIZE,self.head.y),
                      Point(self.head.x-2*BLOCK_SIZE,self.head.y)]
        
        self.score = 0
        self.food = []
        self.turns_hungary = 0

        self.place_food()

    def create_food(self)->tuple[Point,int]:
        ''' generate the location and the type of the food'''
        x = rand.randint(0,(self.width-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
        y = rand.randint(0,(self.height-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
        t = rand.randint(0,1)
        loc = Point(x,y)

        if (loc in self.snake) or (loc in self.food):
            loc,t = self.create_food()

        return loc,t
  
    def place_food(self):
        ''' places the food pellet on the surface'''
        num_food = rand.randint(0,2)
        
        while num_food > 0 and len(self.food) < 3:
            loc,t = self.create_food()

            if t == 0:
                self.food.append(Snail(loc))
            elif t == 1:
                self.food.append(Crab(loc))

            num_food -= 1
        
        if len(self.food) == 0:
            loc,t = self.create_food()

            if t == 0:
                self.food.append(Snail(loc))
            elif t == 1:
                self.food.append(Crab(loc))

    def get_direction_from_action(self,action:Action)->int:
        clock_wise_directions = [Direction.LEFT,Direction.UP,Direction.RIGHT,Direction.DOWN]

        current_heading = clock_wise_directions.index(self.direction)

        if action == Action.LEFT:
            new_heading = (current_heading - 1)%4
        elif action == Action.RIGHT:
            new_heading = (current_heading + 1)%4

        return new_heading
    
    def play_step_AI_train(self,action:int)->tuple[int,bool,int]:
        ''' Basic Game Loop Step for AI-training'''
        self.direction = self.get_direction_from_action(action)
        # move
        self.move(self.direction)
        self.snake.insert(0,self.head)
       
        # check if the game is over 
        game_over:bool = False
        if self.collide_self or self.turns_hungary > 50*len(self.snake):
            game_over = True
        
        # place new food and increase length or just maintain length
        ate_this_round:bool = False
        reward = 0
        for f in self.food:
            if self.head == f.loc:
                # log score improvement
                self.score += f.value
                reward += f.value
                # handle food state
                self.food.remove(f)
                self.place_food()
                # signal the snake ate 
                ate_this_round = True
                # reset turn counter
                self.turns_hungary = 0
        if ate_this_round == False: 
                self.snake.pop()

        # update ui and clock 
        self.update_ui()
        self.clock.tick(SPEED)
        # return to the game over menu and show the score 

        return reward, game_over, self.score

    def play_step_player(self)-> tuple[bool,int]:
        ''' Basic Game Loop Step'''
        # collect user input 
        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                    pyg.quit()
                    quit()
            if event.type == pyg.KEYDOWN:
                if event.key == pyg.K_LEFT:
                    self.direction = Direction.LEFT
                elif event.key == pyg.K_UP:
                    self.direction = Direction.UP
                elif event.key == pyg.K_DOWN:
                    self.direction = Direction.DOWN
                elif event.key == pyg.K_RIGHT:
                    self.direction = Direction.RIGHT
        # move
        self.move(self.direction)
        self.snake.insert(0,self.head)
       
        # check if the game is over 
        game_over:bool = False
        game_over = self.collide_self()
        
        # place new food and increase length or just maintain length
        ate_this_round:bool = False
        for f in self.food:
            if self.head == f.loc:
                self.score += f.value
                self.food.remove(f)
                self.place_food()
                ate_this_round = True
        if ate_this_round == False: 
                self.snake.pop()

        # update ui and clock 
        self.update_ui()
        self.clock.tick(SPEED)
        # return to the game over menu and show the score 

        return game_over, self.score
    
    def update_ui(self):
        ''' updates the pygame display'''
        self.display.fill(GREY)
        
        # snake_head = pyg.image.load("SpriteArt/SnakeHead.png")
        # snake_body = pyg.image.load("SpriteArt/SnakeBody.png")
        # snake_tail= pyg.image.load("SpriteArt/SnakeTail.png")

        crab_ent = pyg.image.load("SpriteArt/crab.png")
        snail_ent = pyg.image.load("SpriteArt/snail.png")
        
        

        for p in self.snake:
            pyg.draw.rect(self.display, CYAN, pyg.Rect(p.x, p.y, BLOCK_SIZE, BLOCK_SIZE))
            pyg.draw.rect(self.display, BLUE, pyg.Rect(p.x+2, p.y+2, BLOCK_SIZE-4, BLOCK_SIZE-4))
        
        for f in self.food:
            if isinstance(f,Crab):
                pyg.Surface.blit(self.display,crab_ent,(f.loc.x,f.loc.y))
            elif isinstance(f,Snail):
                pyg.Surface.blit(self.display,snail_ent,(f.loc.x,f.loc.y))
            else:
                pyg.draw.rect(self.display,BLACK,pyg.rect(f.loc.x,f.loc.y,BLOCK_SIZE,BLOCK_SIZE))


        text = SMALL_FONT.render(f"Score:{self.score}",True,WHITE)
        self.display.blit(text,[5,0])
        pyg.display.flip()

    def move(self,direction):
        ''' decide on the next direction for the snakes head to be moved in'''
        x = self.head.x
        y = self.head.y

        if direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.RIGHT:
            x += BLOCK_SIZE

        #screen wrap 
        if x >= self.width:
            x = 0

        if x < 0:
            x = self.width-BLOCK_SIZE

        if y >= self.height:
            y = 0

        if y < 0:
            y = self.height
        
        self.head = Point(x,y)
    
    def collide_self(self):
        ''' check if the snake has intesected itself '''
        if self.head in self.snake[1:]:
            return True
        else:
            return False

    def game_over_screen(self,score:int):
        ''' display a game over screen'''
        self.display.fill(GREY)
        # generate game over text 
        game_over_text = BIG_FONT.render("Game Over",True,WHITE)
        game_over_text_rect = game_over_text.get_rect(center=(self.width/2,self.height/2))
        # generate score text
        score_text = BIG_FONT.render(f"score:{score}",True,WHITE)
        score_text_rect = score_text.get_rect(center=(self.width/2,2*self.height/3))
        # generate frame
        self.display.blit(game_over_text,game_over_text_rect)
        self.display.blit(score_text,score_text_rect)
        # display
        pyg.display.flip()

        print("Game Over")
    
    def game_start_screen(self)->GameType:
        self.display.fill(GREY)
        # generate player text 
        human_player_text = SMALL_FONT.render("Play with keyboard = q",True,WHITE)
        human_player_text_rect = human_player_text.get_rect(center=(self.width/2,self.height/3))
        # generate AI play text
        AI_player_text = SMALL_FONT.render("Watch AI play = w",True,WHITE)
        AI_player_text_rect = AI_player_text.get_rect(center=(self.width/2,(self.height/3) * 2))
        # generate AI train text 
        AI_train_text = SMALL_FONT.render("Train AI = e",True,WHITE)
        AI_train_text_rect = AI_train_text.get_rect(center=(self.width/2,(self.height/3) * 3))

        #generate frame
        self.display.blit(human_player_text,human_player_text_rect)
        self.display.blit(AI_player_text,AI_player_text_rect)
        self.display.blit(AI_train_text,AI_train_text_rect)

        pyg.display.flip()

        # check input 
        game_type_selected = False
        while game_type_selected == False:
            for event in pyg.event.get():
                if event.type == pyg.KEYDOWN:
                    match event.key:
                        case pyg.K_q:
                            game_type_selected = True
                            return GameType.HUMAN_PLAYER
                        case pyg.K_w:
                            game_type_selected = True
                            return GameType.AI_PLAYER
                        case pyg.K_e:
                            game_type_selected = True
                            return GameType.AI_TRAIN
                        case _:
                            pass

@dataclass
class SnakeFood:
    loc: Point
    color: tuple[int,int,int]
    value: int

@dataclass
class Crab(SnakeFood):
   color:tuple[int,int,int] = RED
   value:int = 15

@dataclass
class Snail(SnakeFood):
    color:tuple[int,int,int] = GREEN
    value:value = 10












if __name__ == '__main__':
    game = SnakeGame()

    #Show Start Screen 

    game_type = game.game_start_screen()

    match game_type:
        case GameType.HUMAN_PLAYER:
            play_step = game.play_step_player
        case GameType.AI_PLAYER:
            play_step = game.play_step_AI_play
        case GameType.AI_TRAIN:
            play_step = game.play_step_AI_train


    #Retrieve action type: player,AI-train,AI-trial

    while True:
        game_over,score = play_step()

        #go to main menu and display score
        if game_over:
            game.game_over_screen(game.score)
            break
    
    pyg.quit()