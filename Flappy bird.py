import pygame
import neat
import time
import os
import random

GEN=0
pygame.font.init() 

width=600
height=800

pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))
bg_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bg.png")))
bird_img = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png"))) for x in range(1,4)]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)


class Bird:
    IMGS=bird_img
    MAX_ROTATION=25
    ROT_VEL=20
    ANIMATION_TIME=5

    def __init__(self,x,y):
        self.x=x
        self.y=y
        self.tilt=0
        self.tick_count=0
        self.vel=0
        self.height=self.y
        self.img_count=0
        self.img=self.IMGS[0]

    def jump(self):
        self.vel= -10.5
        self.tick_count=0
        self.height=self.y

    def move(self):
        self.tick_count+=1
        
        displacement=self.vel*self.tick_count + 1.5*self.tick_count**2

        if displacement>=16: 
            displacement=16
        if displacement<0:
            displacement-=2

        self.y = self.y + displacement
        
        #tilting the bird
        if displacement<0 or self.y<self.height+50:
            if self.tilt<self.MAX_ROTATION:
                self.tilt=self.MAX_ROTATION
        else:
            if self.tilt>-90:
                self.tilt-=self.ROT_VEL
    
    def draw(self,win):
        self.img_count+=1

        if self.img_count<self.ANIMATION_TIME:
            self.img=self.IMGS[0]
        elif self.img_count<self.ANIMATION_TIME*2:
            self.img=self.IMGS[1]
        elif self.img_count<self.ANIMATION_TIME*3:
            self.img=self.IMGS[2]
        elif self.img_count<self.ANIMATION_TIME*4:
            self.img=self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img=self.IMGS[0]
            self.img_count=0

        if self.tilt<=-80:
            self.img=self.IMGS[1]
            self.img_count=self.ANIMATION_TIME*2

        
        rotated_image=pygame.transform.rotate(self.img,self.tilt)
        new_rect=rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x,self.y)).center)
        win.blit(rotated_image,new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface((self.img))


class Pipe():
    """
    represents a pipe object
    """
    GAP = 200
    VEL = 5

    def __init__(self, x):
        """
        initialize pipe object
        :param x: int
        :param y: int
        :return" None
        """
        self.x = x
        self.height = 0

        # where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img

        self.passed = False

        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        # draw top
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # draw bottom
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


    def collide(self, bird, win):
       
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)

        if b_point or t_point:
            return True

        return False

class Base:
    VEL=5
    WIDTH=base_img.get_width()
    IMG=base_img

    def __init__(self,y):
        self.y=y
        self.x1=0
        self.x2=self.WIDTH
    
    def move(self):
        self.x1-=self.VEL
        self.x2-=self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self,win):
        win.blit(self.IMG,(self.x1,self.y))
        win.blit(self.IMG,(self.x2,self.y))

def draw_window(win,birds,pipes,base,score):
    global GEN
    GEN+=1
    
    win.blit(bg_img,(0,0))
    for pipe in pipes:
        pipe.draw(win)
    base.draw(win)

    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (width - score_label.get_width() - 15, 10))

    #gen_label = STAT_FONT.render("Generation: " + str(gen),1,(255,255,255))
    #win.blit(gen_label, (10, 10))

    for bird in birds:
        bird.draw(win)
    pygame.display.update()

def main(genomes,config):
    nets=[]
    ge=[]
    birds=[]
    #id,object
    for _,g in genomes:
        net=neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230,350))
        g.fitness=0
        ge.append(g)

    base=Base(730)
    pipes=[Pipe(700)]
    win=pygame.display.set_mode((width,height))
    run=True
    clock=pygame.time.Clock()
    score=0
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run=False
                pygame.quit()
                quit()

        pipe_ind=0
        if len(birds)>0:
            if len(pipes)>1 and birds[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind+=1
        else:
            run=False
            break

        for x,bird in enumerate(birds):
            bird.move()
            ge[x].fitness+=0.2

            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0]>0.5:
                bird.jump()    


        add_pipe=False
        rem=[]
        for pipe in pipes:
            for x,bird in enumerate(birds):
                if pipe.collide(bird,win):
                    ge[x].fitness -=1.5
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed=True
                    add_pipe=True


            if pipe.x+pipe.PIPE_TOP.get_width()<0:
                rem.append(pipe)

            pipe.move()

        if add_pipe:
            score+=1
            for g in ge:
                g.fitness +=4
            pipes.append(Pipe(700))
        
        for r in rem:
            pipes.remove(r)
        
        for x,bird in enumerate(birds):
            if bird.y + bird.img.get_height()>=730 or bird.y <0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        draw_window(win,birds,pipes,base,score)



def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    # Create the population, which is the top-level object for a NEAT run.
    population = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = population.run(main, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))

if __name__=="__main__":
    local_dir=os.path.dirname(__file__)
    config_path=os.path.join(local_dir,"config.txt")
    run(config_path)
