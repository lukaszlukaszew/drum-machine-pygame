"""App functions"""

import os
from os import listdir
from os.path import isfile, join

import pygame
from pygame import mixer

import ast


def start_app():
    """Preparation of all necessary stuff and main app loop."""

    run = True

    pygame.init()

    info = pygame.display.Info()

    window = {
        "minimum_width": 640,
        "minimum_height": 480,
        "maximum_width": info.current_w,
        "maximum_height": info.current_h,
        "width": 1500,
        "height": 720,
        "frame": 5,
        "window_measurement": 7,
        "title": "Amazing Drum Machine Evolved"
    }

    fonts = {
        "label": pygame.font.Font('freesansbold.ttf', 25),
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
        "save_menu": False,
        "load_menu": False,
        "beat_name": "",
        "typing": False,
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

    screen = pygame.display.set_mode((window["width"], window["height"]), pygame.RESIZABLE)

    pygame.display.set_caption(window["title"])

    samples = load_sounds()
    timer = pygame.time.Clock()

    clicked = [[-1 for _ in range(player["beats"])] for _ in range(len(samples))]

    saved_beats = open_file()

    while run:
        player["beat_length"] = player["fps"] * 60 // player["bpm"]
        timer.tick(player["fps"])
        screen.fill(colors["black"])

        channels = draw_channels(screen, window, colors, fonts, samples)
        boxes = draw_boxes(screen, window, player, colors, clicked, samples)
        buttons = draw_menu(screen, window, colors, fonts, player)

        screen.blit(
            fonts["medium"].render(player[player["playing"]], True, colors["dark_gray"]), (
                2 * window["width"] // 50 + 3 * window["frame"],
                46 * window["height"] // 49
            )
        )

        if player["save_menu"]:
            menu_buttons = draw_save_load("save", screen, window, colors, fonts, player)
        elif player["load_menu"]:
            menu_buttons = draw_save_load("load", screen, window, colors, fonts, player)

        if player["beat_changed"]:
            play_notes(samples, clicked, player["active_beat"])
            player["beat_changed"] = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN and not player["save_menu"] and not player["load_menu"]:
                for _, box in enumerate(boxes):
                    if box[0].collidepoint(event.pos):
                        clicked[box[1][1]][box[1][0]] *= -1
            if event.type == pygame.MOUSEBUTTONUP and not player["save_menu"] and not player["load_menu"]:
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
                elif buttons["save"].collidepoint(event.pos):
                    player["save_menu"] = True
                elif buttons["load"].collidepoint(event.pos):
                    player["load_menu"] = True
                elif buttons["clear"].collidepoint(event.pos):
                    for i in range(len(channels)):
                        samples[i][2] = 1
                        for j in range(player["beats"]):
                            clicked[i][j] = -1

                for i, rect in enumerate(channels):
                    if rect.collidepoint(event.pos):
                        samples[i][2] *= -1

            elif event.type == pygame.MOUSEBUTTONUP:
                if menu_buttons["exit"].collidepoint(event.pos):
                    player["save_menu"] = False
                    player["load_menu"] = False
                    player["beat_name"] = ""
                    player["typing"] = False
                elif player["save_menu"]:
                    if menu_buttons["entry"].collidepoint(event.pos):
                        player["typing"] = not player["typing"]
                    elif menu_buttons["save"].collidepoint(event.pos):
                        save_beat(player, samples, clicked)
                        saved_beats = open_file()
                elif player["load_menu"]:
                    if menu_buttons["load"].collidepoint(event.pos):
                        pass
                    elif menu_buttons["delete"].collidepoint(event.pos):
                        pass

            elif event.type == pygame.TEXTINPUT and player["typing"]:
                player["beat_name"] += event.text

            elif event.type == pygame.KEYDOWN and player["typing"]:
                if event.key == pygame.K_BACKSPACE:
                    player["beat_name"] = player["beat_name"][:-1]

            if event.type == pygame.VIDEORESIZE:
                window["width"] = min(max(window["minimum_width"], event.w), window["maximum_width"])
                window["height"] = min(max(window["minimum_height"], event.h), window["maximum_height"])
                screen = pygame.display.set_mode((window["width"], window["height"]), pygame.RESIZABLE)
                window["frame"] = window["width"] // 300
                fonts["label"] = pygame.font.Font('freesansbold.ttf', window["width"] // 60)
                fonts["medium"] = pygame.font.Font('freesansbold.ttf', window["width"] // 100)

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

    pygame.draw.rect(screen, colors["white"], [0, 0, w, 6 * h + f], f)

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

    # simplyfing calculations

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
        "save": pygame.draw.rect(screen, colors["gray"], [29 * w // 50, 6 * h + 2 * f, 5 * w // 50, h - 4 * f], 0, 2 * f),
        "load": pygame.draw.rect(screen, colors["gray"], [36 * w // 50, 6 * h + 2 * f, 5 * w // 50, h - 4 * f], 0, 2 * f),
        "clear": pygame.draw.rect(screen, colors["gray"], [43 * w // 50, 6 * h + 2 * f, 5 * w // 50, h - 4 * f], 0, 2 * f)
    }

    text = {
        "play_pause": fonts["label"].render("Play/Pause", True, colors["white"]),
        "bpm": fonts["label"].render(f'{player["bpm"]} BPM', True, colors["white"]),
        "bpm_add": fonts["medium"].render("+ 5", True, colors["white"]),
        "bpm_sub": fonts["medium"].render("- 5", True, colors["white"]),
        "beats": fonts["label"].render(f'{player["beats"]} beat{"s" * (1 if player["beats"] else 0)}', True, colors["white"]),
        "beats_add": fonts["medium"].render("+ 1", True, colors["white"]),
        "beats_sub": fonts["medium"].render("- 1", True, colors["white"]),
        "save": fonts["label"].render("Save", True, colors["white"]),
        "load": fonts["label"].render("Load", True, colors["white"]),
        "clear": fonts["label"].render("Clear", True, colors["white"]),
    }

    text_positions = {
        "play_pause": (2 * w // 50 + 3 * f, 6 * h + h // 3 + 2 * f),
        "bpm": (9 * w // 50 + 3 * f, 6 * h + h // 3 + 2 * f),
        "bpm_add": (15 * w // 50 + 3 * f, 6 * h + h // 8 + 2 * f),
        "bpm_sub": (15 * w // 50 + 3 * f, 6 * h + h // 2 + h // 8 + f),
        "beats": (19 * w // 50 + 3 * f, 6 * h + h // 3 + 2 * f),
        "beats_add": (25 * w // 50 + 3 * f, 6 * h + h // 8 + 2 * f),
        "beats_sub": (25 * w // 50 + 3 * f, 6 * h + h // 2 + h // 8 + f),
        "save": (29 * w // 50 + 3 * f, 6 * h + h // 3 + 2 * f),
        "load": (36 * w // 50 + 3 * f, 6 * h + h // 3 + 2 * f),
        "clear": (43 * w // 50 + 3 * f, 6 * h + h // 3 + 2 * f),
    }

    for k, v in text.items():
        screen.blit(v, text_positions[k])

    return buttons


def play_notes(samples, clicked, active_beat):
    """Play choosen sound"""
    for i, click in enumerate(clicked):
        if click[active_beat] == 1 and samples[i][2] == 1:
            samples[i][1].play()


def open_file():
    """Open and parse file"""

    saved_beats = {}

    if "saved_beats.txt" not in os.listdir(os.getcwd()):
        file = open("saved_beats.txt", "x", encoding="utf-8")
        file.close()

    for line in open("saved_beats.txt", "r", encoding="utf-8"):
        name, samples, beats, bpm, clicked = line.split("|||")
        saved_beats[name] = (
            ast.literal_eval(samples),
            int(beats),
            int(bpm),
            ast.literal_eval(clicked)
        )

    return saved_beats


def load_beat():

    # pokazujemy tylko mozliwe do wczytania
    pass


def save_beat(player, samples, clicked):
    """Saving current beat to file"""

    data = f'{player["beat_name"]}' \
           f'|||{[samples[i][0] for i in sorted(samples.keys())]}' \
           f'|||{player["beats"]}' \
           f'|||{player["bpm"]}' \
           f'|||{clicked}\n'

    file = open("saved_beats.txt", "a", encoding="utf-8")

    if file.write(data) == len(data):
        file.close()

    player["save_menu"], player["beat_name"], player["typing"] = False, "", False


def draw_save_load(menu_type, screen, window, colors, fonts, player):
    """Draw save or load menus"""

    # simplyfing calculations

    w = window["width"]
    h = window["height"] // window["window_measurement"]
    f = window["frame"]

    pygame.draw.rect(screen, colors["black"], [0, 0, window["width"], window["height"]])

    menu_buttons = {
        "exit": pygame.draw.rect(screen, colors["gray"], [43 * w // 50, 6 * h + 2 * f, 5 * w // 50, h - 4 * f], 0, 2 * f),
        menu_type: pygame.draw.rect(screen, colors["gray"], [36 * w // 50, 6 * h + 2 * f, 5 * w // 50, h - 4 * f], 0, 2 * f),
    }

    text = {
        "exit": fonts["label"].render("Exit", True, colors["white"]),
        menu_type: fonts["label"].render(menu_type.title(), True, colors["white"])

    }

    text_positions = {
        "exit": (43 * w // 50 + 3 * f, 6 * h + h // 3 + 2 * f),
        menu_type: (36 * w // 50 + 3 * f, 6 * h + h // 3 + 2 * f),
    }

    if menu_type == "save":
        text["save_header"] = fonts["label"].render("SAVE MENU: Please input current beat name", True, colors["white"])
        text_positions["save_header"] = (h, h)

        if player["typing"]:
            color = colors["gray"]
        else:
            color = colors["dark_gray"]

        menu_buttons["entry"] = pygame.draw.rect(screen, color, [w // 4, 7 * h // 4, w // 2, 7 * h // 2], 0, 2 * f)
        text["entry"] = fonts["label"].render(player["beat_name"], True, colors["white"])
        text_positions["entry"] = (w // 4 + 4 * f, 7 * h // 2)

    elif menu_type == "load":

        menu_buttons["delete"] = pygame.draw.rect(screen, colors["gray"], [29 * w // 50, 6 * h + 2 * f, 5 * w // 50, h - 4 * f], 0, 2 * f)
        text["delete"] = fonts["label"].render("Delete", True, colors["white"])
        text_positions["delete"] = (29 * w // 50 + 3 * f, 6 * h + h // 3 + 2 * f)

        menu_buttons["list"] = pygame.draw.rect(screen, colors["gray"], [w // 4, 7 * h // 4, w // 2, 7 * h // 2], f, 2 * f)

        text["load_header"] = fonts["label"].render("LOAD MENU: Please choose beat to load", True, colors["white"])
        text_positions["load_header"] = (h, h)

    for k, v in text.items():
        screen.blit(v, text_positions[k])

    return menu_buttons
