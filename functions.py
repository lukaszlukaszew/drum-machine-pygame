"""App functions"""

import os
from os import listdir
from os.path import isfile, join

import pygame
from pygame import mixer


def start_app():
    """Preparation of all necessary stuff and main app loop."""

    run = True

    pygame.init()

    window = {
        "width": 1500,
        "height": 720,
        "frame": 5,
        "window_measurement": 7,
        "title": "Amazing Drum Machine Evolved"
    }

    fonts = {
        "label": pygame.font.Font('freesansbold.ttf', 20),
        "medium": pygame.font.Font('freesansbold.ttf', 15),
    }

    player = {
        "bpm": 240,
        "fps": 60,
        "beats": 12,
        "active_beat": 0,
        "active_length": 0,
        "playing": True,
        "beat_changed": True,
        "beat_length": None,
        True: "Playing",
        False: "Paused",
    }

    colors = {
        "black": (0, 0, 0),
        "white": (255, 255, 255),
        "gray": (128, 128, 128),
        "gold": (255, 215, 0),
        "green": (0, 255, 0),
        "blue": (0, 255, 255),
        "dark_gray": (50, 50, 50),
        "dark_green": (0, 100, 0),
    }

    screen = pygame.display.set_mode([window["width"], window["height"]])

    pygame.display.set_caption(window["title"])

    samples = load_sounds()
    timer = pygame.time.Clock()

    clicked = [[-1 for _ in range(player["beats"])] for _ in range(len(samples))]

    while run:
        player["beat_length"] = player["fps"] * 60 // player["bpm"]
        timer.tick(player["fps"])
        screen.fill(colors["black"])

        channels = draw_channels(screen, window, colors, fonts, samples)
        boxes = draw_boxes(screen, window, player, colors, clicked, samples)
        buttons = draw_menu(screen, window, colors, fonts, player)

        if player["beat_changed"]:
            play_notes(samples, clicked, player["active_beat"])
            player["beat_changed"] = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for _, box in enumerate(boxes):
                    if box[0].collidepoint(event.pos):
                        clicked[box[1][1]][box[1][0]] *= -1
            if event.type == pygame.MOUSEBUTTONUP:
                if buttons["play_pause"].collidepoint(event.pos):
                    player["playing"] = not player["playing"]
                elif buttons["bpm_add"].collidepoint(event.pos):
                    player["bpm"] = min(600, player["bpm"] + 5)
                elif buttons["bpm_sub"].collidepoint(event.pos):
                    player["bpm"] = max(1, player["bpm"] - 5)
                elif buttons["beats_add"].collidepoint(event.pos):
                    player["beats"] += 1
                    for _, click in enumerate(clicked):
                        click.append(-1)
                elif buttons["beats_sub"].collidepoint(event.pos):
                    player["beats"] = max(1, player["beats"] - 1)
                    for _, click in enumerate(clicked):
                        click.pop()

                for i, rect in enumerate(channels):
                    if rect.collidepoint(event.pos):
                        samples[i][2] *= -1

        screen.blit(
            fonts["medium"].render(player[player["playing"]], True, colors["dark_gray"]), (
                2 * window["width"] // 50 + 3 * window["frame"],
                46 * window["height"] // 49
            )
        )
        if player["playing"]:
            if player["active_length"] < player["beat_length"]:
                player["active_length"] += 1
            else:
                player["active_length"] = 0
                if player["active_beat"] < player["beats"] - 1:
                    player["active_beat"] += 1
                else:
                    player["active_beat"] = 0

                player["beat_changed"] = True

        pygame.display.flip()

    pygame.quit()


def load_sounds():
    """Self-explanatory load sound files"""
    samples = {}

    path = os.getcwd() + "\\sounds\\"

    for i, name in enumerate([f for f in listdir(path) if isfile(join(path, f))]):
        samples[i] = [name[:-4].title(), mixer.Sound(path + name), 1]  # name, mixer.Sound, active

    pygame.mixer.set_num_channels((len(samples) + 1) * 4)

    return samples


def draw_channels(screen, window, colors, fonts, samples):
    """Draw all possible sound channels"""

    # simplyfing code

    w = window["width"] // window["window_measurement"]
    h = window["height"] // window["window_measurement"]
    f = window["frame"]

    instruments = len(samples)

    channels_rects = []

    channels_box = pygame.draw.rect(screen, colors["white"], [0, 0, w, 6 * h + f], f)

    for i in range(instruments):
        channel_rect = pygame.rect.Rect(
            (0, ((6 * h + f) // instruments * i)),
            (w, ((6 * h + f) // instruments ))
        )

        channels_rects.append(channel_rect)

        if samples[i][2] == -1:
            color = colors["gray"]
        else:
            color = colors["white"]

        screen.blit(fonts["label"].render(samples[i][0], True, color),
                    (w // 5, (6 * h + f) // (2 * instruments) * (2 * i + 1) - f))
        if i:
            pygame.draw.line(screen, colors["white"],
                             (f, ((6 * h + f) // instruments * i)),
                             (w - f - 1, ((6 * h + f) // instruments * i)),
                             f)

    return channels_rects


def draw_boxes(screen, window, player, colors, clicked, samples):
    """Draw boxes to represent beat line"""

    # simplyfing code

    w = window["width"] // window["window_measurement"]
    h = window["height"] // window["window_measurement"]
    f = window["frame"]

    beats, instruments = player["beats"], len(clicked)

    boxes = []

    for i in range(beats):
        for j in range(instruments):
            if clicked[j][i] == -1:
                color = colors["gray"]
            elif samples[j][2] == 1:
                color = colors["green"]
            else:
                color = colors["dark_green"]

            rect = pygame.draw.rect(screen, color, [
                w + 6 * w // beats * i + 2 * f,
                (6 * h + f) // instruments * j + 2 * f,
                6 * w // beats - 3 * f,
                (6 * h + f) // instruments - 4 * f
            ], 0)

            pygame.draw.rect(screen, colors["gold"], [
                w + 6 * w // beats * i + f,
                (6 * h + f) // instruments * j + f,
                6 * w // beats - f,
                (6 * h + f) // instruments - 2 * f
            ], f, 2 * f)

            pygame.draw.rect(screen, colors["black"], [
                w + 6 * w // beats * i,
                (6 * h + f) // instruments * j,
                6 * w // beats + f,
                (6 * h + f) // instruments
            ], f, 2 * f)

            boxes.append((rect, (i, j)))

    pygame.draw.rect(screen, colors["blue"], [
        w + 6 * w // beats * player["active_beat"],
        0,
        6 * w // beats + f,
        6 * h
    ], f, 2 * f)

    return boxes


def draw_menu(screen, window, colors, fonts, player):
    """Draw all buttons of bottom menu"""

    # simplyfing code

    w = window["width"]
    h = window["height"] // window["window_measurement"]
    f = window["frame"]

    pygame.draw.rect(screen, colors["white"], [0, 6 * h, w, h], f)

    buttons = {
        "play_pause": pygame.draw.rect(screen, colors["gray"], [2 * w // 50, 6 * h + 2 * f, 5 * w // 50, h - 4 * f], 0, f * 2),
        "bpm": pygame.draw.rect(screen, colors["gray"], [9 * w // 50, 6 * h + 2 * f, 5 * w // 50, h - 4 * f], f, 2 * f),
        "bpm_add": pygame.draw.rect(screen, colors["gray"], [15 * w // 50, 6 * h + 2 * f, 2 * w // 50, h // 2 - 3 * f], 0, 2 * f),
        "bpm_sub": pygame.draw.rect(screen, colors["gray"], [15 * w // 50, 6 * h + h // 2 + f,  2 * w // 50, h // 2 - 3 * f], 0, 2 * f),
        "beats": pygame.draw.rect(screen, colors["gray"], [19 * w // 50, 6 * h + 2 * f, 5 * w // 50, h - 4 * f], f, 2 * f),
        "beats_add": pygame.draw.rect(screen, colors["gray"], [25 * w // 50, 6 * h + 2 * f, 2 * w // 50, h // 2 - 3 * f], 0, 2 * f),
        "beats_sub": pygame.draw.rect(screen, colors["gray"], [25 * w // 50, 6 * h + h // 2 + f, 2 * w // 50, h // 2 - 3 * f], 0, 2 * f),
        "save": pygame.draw.rect(screen, colors["gray"], [29 * w // 50, 6 * h + 2 * f, 5 * w // 50, h - 4 * f], f, 2 * f),
        "load": pygame.draw.rect(screen, colors["gray"], [36 * w // 50, 6 * h + 2 * f, 5 * w // 50, h - 4 * f], f, 2 * f),
        "clear": pygame.draw.rect(screen, colors["gray"], [43 * w // 50, 6 * h + 2 * f, 5 * w // 50, h - 4 * f], f, 2 * f)
    }

    text = {
        "play_pause": fonts["label"].render("Play/Pause", True, colors["white"]),
        "bpm": fonts["label"].render(f'{player["bpm"]} BPM', True, colors["white"]),
        "bpm_add": fonts["medium"].render("+ 5", True, colors["white"]),
        "bpm_sub": fonts["medium"].render("- 5", True, colors["white"]),
        "beats": fonts["label"].render(f'{player["beats"]} beat{"s" * (1 if player["beats"] else 0)}', True, colors["white"]),
        "beats_add": fonts["medium"].render("+ 1", True, colors["white"]),
        "beats_sub": fonts["medium"].render("- 1", True, colors["white"]),
        #"save": (),
        #"load": (),
        #"clear": (),
    }

    text_positions = {
        "play_pause": (2 * w // 50 + 3 * f, 6 * h + h // 3 + 2 * f),
        "bpm": (9 * w // 50 + 3 * f, 6 * h + h // 3 + 2 * f),
        "bpm_add": (15 * w // 50 + 3 * f, 6 * h + h // 8 + 2 * f),
        "bpm_sub": (15 * w // 50 + 3 * f, 6 * h + h // 2 + h // 8 + f),
        "beats": (19 * w // 50 + 3 * f, 6 * h + h // 3 + 2 * f),
        "beats_add": (25 * w // 50 + 3 * f, 6 * h + h // 8 + 2 * f),
        "beats_sub": (25 * w // 50 + 3 * f, 6 * h + h // 2 + h // 8 + f),
        "save": (2000, 2000),
        "load": (2000, 2000),
        "clear": (2000, 2000),
    }

    for k, v in text.items():
        screen.blit(v, text_positions[k])

    return buttons


def play_notes(samples, clicked, active_beat):
    """Play choosen sound"""
    for i, click in enumerate(clicked):
        if click[active_beat] == 1 and samples[i][2] == 1:
            samples[i][1].play()
