import random  # For generating random numbers
import sys  # We will use sys.exit to exit the program
import pygame
import pygame.freetype
from pygame.locals import *  # Basic pygame imports
import os
import json
import speech_recognition as sr
import threading

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init()

voice_jump = False
HIGHSCORE_FILE = 'highscore.json'

# Global Variables for the game
FPS = 32
scr_width = 288
scr_height = 512
display_screen_window = pygame.display.set_mode((scr_width, scr_height))
play_ground = scr_height * 0.8
game_image = {}
game_audio_sound = {}
player = 'images/bird.png'
bcg_image = 'images/background.png'
pipe_image = 'images/pipe.png'


def welcome_main_screen():
    """
    Shows welcome images on the screen
    """
    display_screen_window = pygame.display.set_mode((scr_width, scr_height))
    highscore = load_highscore()
    font = pygame.font.SysFont('Arial', 18)
    text_surface = font.render(f"Highscore: {highscore}", True, (255, 255, 255))
    display_screen_window.blit(text_surface, (10, 10))
    p_x = int(scr_width / 5)
    p_y = int((scr_height - game_image['player'].get_height()) / 2)
    msgx = int((scr_width - game_image['message'].get_width()) / 2)
    msgy = int(0)
    b_x = 0
    while True:
        for event in pygame.event.get():
            # if user clicks on cross button, close the game
            if event.type == QUIT:
                graceful_exit()

            # If the user presses space or up key, start the game for them
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if confirm_quit(): # show the confirmation dialogue
                        graceful_exit()
                elif event.key in (K_SPACE, K_UP):
                    return
            else:
                display_screen_window.blit(game_image['background'], (0, 0))
                display_screen_window.blit(game_image['player'], (p_x, p_y))
                display_screen_window.blit(game_image['message'], (msgx, msgy))
                display_screen_window.blit(game_image['base'], (b_x, play_ground))
                pygame.display.update()
                time_clock.tick(FPS)

voice_jump = False
HIGHSCORE_FILE = 'highscore.json'

def voice_command_listener():
    global voice_jump
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
    while True:
        try:
            with mic as source:
                audio = recognizer.listen(source, phrase_time_limit=1)
            text = recognizer.recognize_google(audio)
            if 'jump' in text.lower():
                voice_jump = True
        except sr.UnknownValueError:
            continue
        except sr.RequestError:
            break

def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, 'r') as file:
            return json.load(file).get('highscore', 0)
    return 0

def save_highscore(score):
    highscore = load_highscore()
    if score > highscore:
        with open(HIGHSCORE_FILE, 'w') as file:
            json.dump({'highscore': score}, file)

def confirm_quit():
    #inializes new free type
    if not pygame.freetype.get_init():
        pygame.freetype.init()
    
    # create a semi-transpart overlay
    overlay = pygame.Surface((scr_width, scr_height), pygame.SRCALPHA)
    overlay.fill((0,0,0, 180)) # black but transparent, come back and play with levels see what feels right
    display_screen_window.blit(overlay, (0,0))

    # load font
    try:
        font = pygame.freetype.SysFont('Arial', 30)
    except:
        font = pygame.freetype.SysFont(None, 30) #falling back to default if it doenst work, remove later Dylan

    # make some text actally come on screen, returns surface and rect
    text_surface, text_rect = font.render(
        "Quit Game? (Y/N)",
        (255, 255, 255) # white, can be changed later also
    )
    text_rect.center = (scr_width//2, scr_height//2) # centers text
    display_screen_window.blit(text_surface, text_rect) # overlays new display
    pygame.display.update() 

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return True
            if event.type == KEYDOWN:
                if event.key == K_y:
                    return True
                elif event.key == K_n:
                    return False
        time_clock.tick(FPS)

def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, 'r') as file:
            return json.load(file).get('highscore', 0)
    return 0

def save_highscore(score):
    highscore = load_highscore()
    if score > highscore:
        with open(HIGHSCORE_FILE, 'w') as file:
            json.dump({'highscore': score}, file)

def graceful_exit():
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    pygame.quit()
    sys.exit(0)

def main_gameplay():
    global voice_jump
    score = 0
    p_x = int(scr_width / 5)
    p_y = int(scr_width / 2)
    b_x = 0

    n_pip1 = get_Random_Pipes()
    n_pip2 = get_Random_Pipes()

    up_pips = [
        {'x': scr_width + 200, 'y': n_pip1[0]['y']},
        {'x': scr_width + 200 + (scr_width / 2), 'y': n_pip2[0]['y']},
    ]

    low_pips = [
        {'x': scr_width + 200, 'y': n_pip1[1]['y']},
        {'x': scr_width + 200 + (scr_width / 2), 'y': n_pip2[1]['y']},
    ]

    pip_Vx = -4

    p_vx = -9
    p_mvx = 10
    p_mvy = -8

    p_accuracy = 1

    p_flap_accuracy = -8
    p_flap = False

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                graceful_exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                if confirm_quit():
                    graceful_exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if p_y > 0:
                    p_vx = p_flap_accuracy
                    p_flap = True
                    game_audio_sound['wing'].play()

        cr_tst = is_Colliding(p_x, p_y, up_pips,
                              low_pips)
        
        '''
        added in way to freeze physics upon collision so bird doesn't
        continue to move into pipe after colliding
        
        also added in new behavior for game over/collision with a pipe
        '''
        if cr_tst:
            fall_velocity = 0
            gravity = 0.75        
            max_fall_speed = 5
            p_y = float(p_y)
            
            # temporarily freeze bird sprite on screen
            display_screen_window.blit(game_image['background'], (0, 0))
            for pip_upper, pip_lower in zip(up_pips, low_pips):
                display_screen_window.blit(game_image['pipe'][0], (pip_upper['x'], pip_upper['y']))
                display_screen_window.blit(game_image['pipe'][1], (pip_lower['x'], pip_lower['y']))

            display_screen_window.blit(game_image['base'], (b_x, play_ground))
            display_screen_window.blit(game_image['player'], (p_x, p_y))            
            
            pygame.display.update()
            pygame.time.delay(100)
            
            while p_y < play_ground - game_image['player'].get_height():
                fall_velocity = min(fall_velocity + gravity, max_fall_speed)
                p_y += fall_velocity

                display_screen_window.blit(game_image['background'], (0, 0))
                for pip_upper, pip_lower in zip(up_pips, low_pips):
                    display_screen_window.blit(game_image['pipe'][0], (pip_upper['x'], pip_upper['y']))
                    display_screen_window.blit(game_image['pipe'][1], (pip_lower['x'], pip_lower['y']))
                display_screen_window.blit(game_image['base'], (b_x, play_ground))
                
                # flip bird sprite
                flipped_bird = pygame.transform.flip(game_image['player'], False, True)
                display_screen_window.blit(flipped_bird, (p_x, int(p_y)))

                # drawing score
                d = [int(x) for x in list(str(score))]
                w = 0
                for digit in d:
                    w += game_image['numbers'][digit].get_width()
                Xoffset = (scr_width - w) / 2
                for digit in d:
                    display_screen_window.blit(game_image['numbers'][digit], (Xoffset, scr_height * 0.12))
                    Xoffset += game_image['numbers'][digit].get_width()

                pygame.display.update()
                time_clock.tick(60)

            return
        

        p_middle_positions = p_x + game_image['player'].get_width() / 2
        for pipe in up_pips:
            pip_middle_positions = pipe['x'] + game_image['pipe'][0].get_width() / 2
            if pip_middle_positions <= p_middle_positions < pip_middle_positions + 4:
                score += 1
                print(f"Your score is {score}")
                game_audio_sound['point'].play()

        if p_vx < p_mvx and not p_flap:
            p_vx += p_accuracy

        if p_flap:
            p_flap = False
        p_height = game_image['player'].get_height()
        p_y = p_y + min(p_vx, play_ground - p_y - p_height)

        for pip_upper, pip_lower in zip(up_pips, low_pips):
            pip_upper['x'] += pip_Vx
            pip_lower['x'] += pip_Vx

        if 0 < up_pips[0]['x'] < 5:
            new_pip = get_Random_Pipes()
            up_pips.append(new_pip[0])
            low_pips.append(new_pip[1])

        if up_pips[0]['x'] < -game_image['pipe'][0].get_width():
            up_pips.pop(0)
            low_pips.pop(0)

        display_screen_window.blit(game_image['background'], (0, 0))
        for pip_upper, pip_lower in zip(up_pips, low_pips):
            display_screen_window.blit(game_image['pipe'][0], (pip_upper['x'], pip_upper['y']))
            display_screen_window.blit(game_image['pipe'][1], (pip_lower['x'], pip_lower['y']))

        display_screen_window.blit(game_image['base'], (b_x, play_ground))
        display_screen_window.blit(game_image['player'], (p_x, p_y))
        d = [int(x) for x in list(str(score))]
        w = 0
        for digit in d:
            w += game_image['numbers'][digit].get_width()
        Xoffset = (scr_width - w) / 2

        for digit in d:
            display_screen_window.blit(game_image['numbers'][digit], (Xoffset, scr_height * 0.12))
            Xoffset += game_image['numbers'][digit].get_width()
        pygame.display.update()
        time_clock.tick(FPS)
        save_highscore(score)

def is_Colliding(p_x, p_y, up_pipes, low_pipes):
    '''
    adjusting player hit box to be more accurate to sprite image, to help with clipping issues
    '''
    
    player_hitbox = pygame.Rect(
        p_x,
        p_y + 0.5,
        game_image['player'].get_width(),
        game_image['player'].get_height() + 1
    )
    
    
    if p_y > play_ground - 25 or p_y < 0:
        game_audio_sound['hit'].play()
        return True

    for pipe in up_pipes:
        pipe_hitbox = pygame.Rect(
            pipe['x'],
            pipe['y'],
            game_image['pipe'][0].get_width(),
            game_image['pipe'][0].get_height()
        )
        if player_hitbox.colliderect(pipe_hitbox):
            game_audio_sound['hit'].play()
            return True

    for pipe in low_pipes:
        pipe_hitbox = pygame.Rect(
            pipe['x'],
            pipe['y'],
            game_image['pipe'][1].get_width(),
            game_image['pipe'][1].get_height()
        )
        if player_hitbox.colliderect(pipe_hitbox):
            game_audio_sound['hit'].play()
            return True

    return False


def get_Random_Pipes():
    """
    Generate positions of two pipes(one bottom straight and one top rotated ) for belittling on the screen
    """
    pip_h = game_image['pipe'][0].get_height()
    off_s = scr_height / 3
    yes2 = off_s + random.randrange(0, int(scr_height - game_image['base'].get_height() - 1.2 * off_s))
    pipeX = scr_width + 10
    y1 = pip_h - yes2 + off_s
    pipe = [
        {'x': pipeX, 'y': -y1},  # upper Pipe
        {'x': pipeX, 'y': yes2}  # lower Pipe
    ]
    return pipe
def graceful_exit():
    "more safely shuts down pygame"
    pygame.mixer.quit()
    pygame.quit()
    sys.exit(0)



if __name__ == "__main__":

    pygame.init()
    time_clock = pygame.time.Clock()
    pygame.display.set_caption('Flappy Bird Game')
    game_image['numbers'] = (
        pygame.image.load('images/0.png').convert_alpha(),
        pygame.image.load('images/1.png').convert_alpha(),
        pygame.image.load('images/2.png').convert_alpha(),
        pygame.image.load('images/3.png').convert_alpha(),
        pygame.image.load('images/4.png').convert_alpha(),
        pygame.image.load('images/5.png').convert_alpha(),
        pygame.image.load('images/6.png').convert_alpha(),
        pygame.image.load('images/7.png').convert_alpha(),
        pygame.image.load('images/8.png').convert_alpha(),
        pygame.image.load('images/9.png').convert_alpha(),
    )

    game_image['message'] = pygame.image.load('images/message.png').convert_alpha()
    game_image['base'] = pygame.image.load('images/base.png').convert_alpha()
    game_image['pipe'] = (pygame.transform.rotate(pygame.image.load(pipe_image).convert_alpha(), 180),
                          pygame.image.load(pipe_image).convert_alpha()
                          )

    # Game sounds
    pygame.mixer.music.load('sounds/bgm.mp3')
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    threading.Thread(target=voice_command_listener, daemon=True).start()
    game_audio_sound['die'] = pygame.mixer.Sound('sounds/die.wav')
    game_audio_sound['hit'] = pygame.mixer.Sound('sounds/hit.wav')
    game_audio_sound['point'] = pygame.mixer.Sound('sounds/point.wav')
    game_audio_sound['swoosh'] = pygame.mixer.Sound('sounds/swoosh.wav')
    game_audio_sound['wing'] = pygame.mixer.Sound('sounds/wing.wav')

    game_image['background'] = pygame.image.load(bcg_image).convert()
    game_image['player'] = pygame.image.load(player).convert_alpha()

    while True:
        welcome_main_screen()  # Shows welcome screen to the user until he presses a button
        main_gameplay()  # This is the main game function
