import pygame
import random
import os
import time
import neat

pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans",30)

WIN_WIDTH = 400
WIN_HEIGHT = 600
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")
GEN = 0

BIRD_IMGS = [pygame.image.load(os.path.join("img","bird1.png")),
             pygame.image.load(os.path.join("img","bird2.png")),
             pygame.image.load(os.path.join("img","bird3.png"))]
PIPE_IMG = pygame.transform.scale(pygame.image.load(os.path.join("img","pipe.png")),(60,400))
BASE_IMG = pygame.transform.scale(pygame.image.load(os.path.join("img","base.png")),(400,112))
BG_IMG = pygame.transform.scale(pygame.image.load(os.path.join("img","bg.png")),(400,600))

DRAW_LINES = True

class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 20
    ROT_VEL = 10
    ANIMATION_TIME = 5

    #Initialize the bird
    def __init__(self, x, y):
        #Coordinate
        self.x = x
        self.y = y
        self.tilt = 0  #Degree to tilt
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    #A little physics here for the gravitation of the bird    
    def jump(self):
        self.vel = -9
        self.tick_count = 0
        self.height = self.y

    #A little physics again :V d represents the displacement of the bird    
    def move(self):
        self.tick_count += 1
        #for downward acceleration
        d = self.vel*self.tick_count + 0.5*3*(self.tick_count)**2 #calculate displacement
        #terminal velocity
        if d >= 16 :
            d = (d/abs(d)) * 16
        if d < 0 :
            d -= 2
        self.y = self.y + d
        if d < 0 or self.y < self.height + 50 : #tilt up
            if self.tilt < self.MAX_ROTATION :
                self.tilt = self.MAX_ROTATION
        else :                                  #tilt down
            if self.tilt > -90 :
                self.tilt -= self.ROT_VEL
                
    def draw(self, win) :
        self.img_count += 1

        #For the flapping animation of the bird, loop continuously 3 images
        if self.img_count <= self.ANIMATION_TIME :
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME * 2 :
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME * 3 :
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME * 4 :
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1 :
            self.img = self.IMGS[0]
            self.img_count = 0
        #when bird is nose diving it isnt flapping
        if self.tilt <= -80 :
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2
        # tilt the bird
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)
        
    #Get the mask for the current image of the bird    
    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe :
    GAP = 120
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
    
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True) 
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        #set randomly the height of each pipe
        self.height = random.randrange(100,300)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    #move pipe based on VEL
    def move(self):
        self.x -= self.VEL

    #draw both the top and bottom of the pipe
    def draw(self, win) :
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    #return true if birds collide with a pipe
    def collide(self, bird):
        bird_mask = bird.get_mask()
        
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        t_point = bird_mask.overlap(top_mask, top_offset)
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)

        if (t_point or b_point):
            return True
        
        return False


class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    #move the ground so it looks like scrolling
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0 :
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0 :
            self.x2 = self.x1 + self.WIDTH

    #draw the ground (2 images consecutively)
    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))
            
def draw_window(win, birds, pipes, base, score, GEN, pipe_ind):
    if GEN == 0:
        GEN = 1
    win.blit(BG_IMG, (0,0))
    for pipe in pipes:
        pipe.draw(win)
    base.draw(win)
    
    #score
    text = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(text,(WIN_WIDTH - 10 - text.get_width(), 10))
    #generation
    text = STAT_FONT.render("Gen: " + str(GEN-1),1,(255,255,255))
    win.blit(text,(10, 10))
    #alive
    text = STAT_FONT.render("Alive: " + str(len(birds)),1,(255,255,255))
    win.blit(text,(10, 30))

    #draw lines from bird to pipes
    for bird in birds:
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255,0,0),
                                 (bird.x+bird.img.get_width()/2,
                                  bird.y + bird.img.get_height()/2),
                                 (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2,
                                  pipes[pipe_ind].height), 5)
                pygame.draw.line(win, (255,0,0),
                                 (bird.x+bird.img.get_width()/2,
                                  bird.y + bird.img.get_height()/2),
                                 (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2,
                                  pipes[pipe_ind].bottom), 5)
            except:
                pass
        bird.draw(win)
    pygame.display.update()

def eval_genomes(genomes, config):
    global GEN, WIN
    GEN += 1
    win = WIN
    
    nets = []
    ge = []
    birds = []

    for _,g in genomes :
        #start with fitness level of 0
        g.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(150,250))
        ge.append(g)
    
    base = Base(530)
    pipes = [Pipe(400)]
    clock = pygame.time.Clock()
    score = 0
    run = True
    
    while run and len(birds) > 0:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break
            
        pipe_ind = 0
        if len(birds) > 0:
            #decide whether to use the first or second pipe on the screen for neural network inpit
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        
        for x, bird in enumerate(birds):
            bird.move()
            #give each bird a fitness of 0.1 for each time it stays alive
            ge[x].fitness += 0.1
            #send bird, top pipe and bottom pipe location to decide whether to jump or not
            output = nets[x].activate((bird.y,
                                       abs(bird.y - pipes[pipe_ind].height),
                                       abs(bird.y - pipes[pipe_ind].bottom)))
            #Use a hyperbolic tangent function so result will be between -1 and 1
            #If over 0.5 jump
            if output[0] > 0.5:
                bird.jump()

        base.move()
        
        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                if not pipe.passed and pipe.x < bird.x :
                    pipe.passed = True
                    add_pipe = True
            if pipe.x + pipe.PIPE_TOP.get_width() < 0 :
                rem.append(pipe)   
            pipe.move()
            
        if add_pipe :
            score += 1
            # give birds which pass through a pipe a reward (not necessary)
            # for g in ge:
            #     g.fitness += 5
            pipes.append(Pipe(400))
            
        for r in rem :
            pipes.remove(r)
            
        #if a bird(s) die(s), remove it/them from the screen
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 530 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        draw_window(win, birds, pipes, base, score, GEN, pipe_ind)
        
        #break if score gets large enough
        if score >= 50:
            break
        

#Run the NEAT algorithm to train a neural network to play
#config_path = location of config file
def run(config_file):
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_file)

    #Create the population, which is the number of birds for each NEAT run
    p = neat.Population(config)

    #Show progress in the terminal
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    #Run for up to 50 generations
    winner = p.run(eval_genomes, 50)
    
    #Show final stats
    print('\nBest genome:\n{!s}'.format(winner))
    
if __name__ == '__main__' :
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
