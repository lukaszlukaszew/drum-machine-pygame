"""Custom Drum Machine"""

import pygame
#from pygame import mixer

pygame.init()  # module tools initialization

# TODO modification: set resolution based on system settings
# TODO modification: full screen on, off and swiitching with background
# TODO modification: adding instrument (limit, scroll above the limit, choosing music file)

width, height, frame = 860, 720, 5

# basic colors of project
black = (0, 0, 0)
white = (255, 255, 255)
gray = (128, 128, 128)
gold = (255, 215, 0)

screen = pygame.display.set_mode([width, height])
pygame.display.set_caption("Amazing Drum Machine Evolved")

# TODO choose better font
# TODO modification: checking some fonts installed and choosing the proper one
# TODO modification: adjust size of the font according to screen size

label_font = pygame.font.Font('freesansbold.ttf', 15)

# TODO knowledge: what do below thingy?
fps = 60
timer = pygame.time.Clock()


beats = 22
instruments = 6


def draw_grid():
    left_box = pygame.draw.rect(screen, white, [0, 0, width // 7, height // 7 * 6 + frame], frame)
    bottom_box = pygame.draw.rect(screen, white, [0, height // 7 * 6, width, height // 7], frame)
    boxes = []
    colors = [gray, white, gray]

    # TODO: clean below code... how it looks jeeez...
    # TODO: modification: upgrade resizing

    samples = []

    samples.append(label_font.render('Hi hat', True, white))
    samples.append(label_font.render('Snare', True, white))
    samples.append(label_font.render('Kick', True, white))
    samples.append(label_font.render('Crash', True, white))
    samples.append(label_font.render('Floor', True, white))
    samples.append(label_font.render('Clap', True, white))

    instr = min(len(samples), instruments)

    for i in range(instr):
        screen.blit(samples[i], (30, (height // 7 * 6 + frame) // (2 * instr) * (2 * i + 1) - frame))
        if i:
            pygame.draw.line(screen, white, (frame, ((height // 7 * 6 + frame) // (2 * instr) * i * 2)),
                             (width // 7 - frame - 1, ((height // 7 * 6 + frame) // (2 * instr) * i * 2)), frame)

    # to remember: rect is drawn by start x, y and than width and height, not ending x, y

    for i in range(beats):
        for j in range(instr):
            rect = pygame.draw.rect(screen, gold, [
                width // 7 + width // 7 * 6 // beats * i,
                (height // 7 * 6 + frame) // (2 * instr) * j * 2,
                width // 7 * 6 // beats + frame,
                (height // 7 * 6 + frame) // instr
            ], 5, 10)


run = True

while run:
    timer.tick(fps)
    screen.fill(black)
    draw_grid()

    # this parts captures all the events that occure in PYGAME
    # TODO knowledge: what are possible events in PYGAME?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.flip()

pygame.quit()

# TODO modyfication: how to make this OOP?
# TODO modification: implement proper documentation
