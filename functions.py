"""App functions"""

import os
from os import listdir
from os.path import isfile, join

import pygame
from pygame import mixer

import configuration as c
import rgb as r


def start_app():
    """Preparation of all necessary stuff and main app loop."""
    active_beat, active_length, playing, beat_changed, beats = 0, 0, True, True, c.beats
    beat_length = c.fps * 60 // c.bpm
    run = True

    pygame.init()

    screen = pygame.display.set_mode([c.width, c.height])
    label_font = pygame.font.Font('freesansbold.ttf', 15)
    pygame.display.set_caption("Amazing Drum Machine Evolved")

    samples = load_sounds()
    timer = pygame.time.Clock()

    clicked = [[-1 for _ in range(c.beats)] for _ in range(len(samples))]

    while run:
        timer.tick(c.fps)
        screen.fill(r.black)
        boxes = draw_grid(label_font, beats, screen, samples, clicked, active_beat)
        # play_pouse = pygame.draw.rect(screen, gray, [50, c.height - 150, 200, 100], 0, 5)
        if beat_changed:
            play_notes(samples, clicked, active_beat)
            beat_changed = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, box in enumerate(boxes):
                    if box[0].collidepoint(event.pos):
                        coords = box[1]
                        clicked[coords[1]][coords[0]] *= -1

        if playing:
            if active_length < beat_length:
                active_length += 1
            else:
                active_length = 0
                if active_beat < c.beats - 1:
                    active_beat += 1
                    beat_changed = True
                else:
                    active_beat = 0
                    beat_changed = True

        pygame.display.flip()

    pygame.quit()


def load_sounds():
    """Self-explanatory load sound files"""
    samples = {}

    path = os.getcwd() + "\\sounds\\"

    for i, name in enumerate([f for f in listdir(path) if isfile(join(path, f))]):
        samples[i] = (name[:-4].title(), mixer.Sound(path + name))

    pygame.mixer.set_num_channels((len(samples)+1) * 4)

    return samples


def draw_grid(label_font, beats, screen, samples, clicked, active_beat):
    """Prepare all things visible on the screen"""
    left_box = pygame.draw.rect(screen, r.white, [0, 0, c.width // 7, c.height // 7 * 6 + c.frame], c.frame)
    bottom_box = pygame.draw.rect(screen, r.white, [0, c.height // 7 * 6, c.width, c.height // 7], c.frame)
    boxes, instruments = [], len(samples)

    for i in range(instruments):
        screen.blit(label_font.render(samples[i][0], True, r.white),
                    (30, (c.height // 7 * 6 + c.frame) // (2 * instruments) * (2 * i + 1) - c.frame))
        if i:
            pygame.draw.line(screen, r.white, (c.frame, ((c.height // 7 * 6 + c.frame) // (2 * instruments) * i * 2)),
                             (c.width // 7 - c.frame - 1, ((c.height // 7 * 6 + c.frame) // (2 * instruments) * i * 2)),
                             c.frame)

    for i in range(beats):
        for j in range(instruments):
            if clicked[j][i] == -1:
                color = r.gray
            else:
                color = r.green

            rect = pygame.draw.rect(screen, color, [
                c.width // 7 + c.width // 7 * 6 // beats * i + c.frame * 2,
                (c.height // 7 * 6 + c.frame) // (2 * instruments) * j * 2 + c.frame * 2,
                c.width // 7 * 6 // beats + c.frame - 2 * c.frame * 2,
                (c.height // 7 * 6 + c.frame) // instruments - 2 * c.frame * 2
            ], 0)

            pygame.draw.rect(screen, r.gold, [
                c.width // 7 + c.width // 7 * 6 // beats * i + c.frame,
                (c.height // 7 * 6 + c.frame) // (2 * instruments) * j * 2 + c.frame,
                c.width // 7 * 6 // beats + c.frame - 2 * c.frame,
                (c.height // 7 * 6 + c.frame) // instruments - 2 * c.frame
            ], c.frame, 2 * c.frame)

            pygame.draw.rect(screen, r.black, [
                c.width // 7 + c.width // 7 * 6 // beats * i,
                (c.height // 7 * 6 + c.frame) // (2 * instruments) * j * 2,
                c.width // 7 * 6 // beats + c.frame,
                (c.height // 7 * 6 + c.frame) // instruments
            ], c.frame, 2 * c.frame)

            boxes.append((rect, (i, j)))

    active = pygame.draw.rect(screen, r.blue, [
        c.width // 7 + c.width // 7 * 6 // beats * active_beat,
        0,
        c.width // 7 * 6 // beats + c.frame,
        (c.height // 7 * 6 + c.frame) - c.frame
    ], c.frame, 2 * c.frame)

    return boxes


def play_notes(samples, clicked, active_beat):
    """Play choosen sound"""
    for i, click in enumerate(clicked):
        if click[active_beat] == 1:
            samples[i][1].play()
