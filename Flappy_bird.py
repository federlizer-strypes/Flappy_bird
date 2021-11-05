import sys, pygame, random

from pygame.locals import *


def base_move():
    game_display.blit(base, (base_x_position, 900))
    game_display.blit(base, (base_x_position + 576, 900))


def create_pipe():
    random_pipe_pos = random.choice(pipe_height)
    bottom_pipe = pipe_surface.get_rect(midtop=(700, random_pipe_pos))
    top_pipe = pipe_surface.get_rect(midbottom=(700, random_pipe_pos - 300))
    return bottom_pipe, top_pipe


def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 5
    visible_pipes = [pipe for pipe in pipes if pipe.right > - 50]
    return visible_pipes


def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= 1024:
            game_display.blit(pipe_surface, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_surface, False, True)
            game_display.blit(flip_pipe, pipe)


def check_collision(pipes):
    global can_score
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            hit_sound.play()
            can_score = True
            return False

    if bird_rect.top <= -100 or bird_rect.bottom >= 880:
        death_sound.play()
        can_score = True
        return False

    return True


def rotate_bird(bird):
    new_bird = pygame.transform.rotozoom(bird, -bird_movement * 3, 1)
    return new_bird


def bird_animation():
    new_bird = bird_frames[bird_index]
    new_bird_rect = new_bird.get_rect(center=(100, bird_rect.centery))

    return new_bird, new_bird_rect


def score_display(game_state):
    if game_state == 'main_game':
        score_surface = game_font.render(str(score), True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(288, 100))
        game_display.blit(score_surface, score_rect)
    if game_state == 'game_over':
        score_surface = game_font.render(f"Score: {str(score)}", True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(288, 100))
        game_display.blit(score_surface, score_rect)

        high_score_surface = game_font.render(f"High Score: {str(high_score)}", True, (255, 255, 255))
        high_score_rect = high_score_surface.get_rect(center=(288, 800))
        game_display.blit(high_score_surface, high_score_rect)


def score_check():
    global score, can_score
    if pipe_list:
        for pipe in pipe_list:
            if 95 < pipe.centerx < 105 and can_score:
                score += 1
                score_sound.play()
                can_score = False
            if pipe.centerx < 0:
                can_score = True


def update_score(score, high_score):
    if score > high_score:
        high_score = score
    return high_score


pygame.init()
# Display size
display_width = 576
display_height = 1024
game_display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Flappy Bird')
speed = pygame.time.Clock()
game_font = pygame.font.Font('resources/04B_19.TTF', 40)

# Game variables
gravity = 0.25
bird_movement = 0
game_active = True
score = 0
high_score = 0
can_score = True

# Background image
background = pygame.image.load('resources/background-day.png').convert()
background = pygame.transform.scale2x(background)

# Base image
base = pygame.image.load('resources/base.png').convert()
base = pygame.transform.scale2x(base)
base_x_position = 0

# Pipes images
pipe_surface = pygame.image.load('resources/pipe-green.png').convert()
pipe_surface = pygame.transform.scale2x(pipe_surface)
pipe_list = []
spawn_pipe = pygame.USEREVENT
pygame.time.set_timer(spawn_pipe, 1200)
pipe_height = [400, 600, 800]

# Bird image
bird_downflap = pygame.transform.scale2x(pygame.image.load('resources/bluebird-downflap.png').convert_alpha())
bird_midflap = pygame.transform.scale2x(pygame.image.load('resources/bluebird-midflap.png').convert_alpha())
bird_upflap = pygame.transform.scale2x(pygame.image.load('resources/bluebird-upflap.png').convert_alpha())
bird_frames = [bird_downflap, bird_midflap, bird_upflap]
bird_index = 2
bird = bird_frames[bird_index]
bird_rect = bird.get_rect(center=(100, 512))
bird_flap = pygame.USEREVENT + 1
pygame.time.set_timer(bird_flap, 200)

# Game over screen
game_over_surface = pygame.transform.scale2x(pygame.image.load('resources/message.png').convert_alpha())
game_over_rect = game_over_surface.get_rect(center=(288, 512))

# Game Sounds
flap_sound = pygame.mixer.Sound('resources/wing.wav')
death_sound = pygame.mixer.Sound('resources/die.wav')
hit_sound = pygame.mixer.Sound('resources/hit.wav')
score_sound = pygame.mixer.Sound('resources/point.wav')

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_SPACE and game_active:
                bird_movement = 0
                bird_movement -= 8.5
                flap_sound.play()
            if event.key == K_SPACE and game_active is False:
                game_active = True
                pipe_list.clear()
                bird_rect.center = (100, 512)
                bird_movement = 0
                score = 0
        if event.type == spawn_pipe:
            pipe_list.extend(create_pipe())
        if event.type == bird_flap:
            if bird_index < 2:
                bird_index += 1
            else:
                bird_index = 0

            bird, bird_rect = bird_animation()

    game_display.blit(background, (0, 0))
    if game_active:
        # Bird move
        bird_movement += gravity
        rotated_bird = rotate_bird(bird)
        bird_rect.centery += bird_movement
        game_display.blit(rotated_bird, bird_rect)
        game_active = check_collision(pipe_list)

        # Pipe move
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)

        # Score
        score_display('main_game')
        score_check()
    else:
        high_score = update_score(score, high_score)
        game_display.blit(game_over_surface, game_over_rect)
        score_display('game_over')

    # Floor move
    base_x_position -= 1
    base_move()
    if base_x_position <= -576:
        base_x_position = 0

    pygame.display.update()
    speed.tick(120)
