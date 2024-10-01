import pygame
import random
import math

pygame.init()

width, height = 500, 700
screen = pygame.display.set_mode((width, height))

r = 15
x1, y1 = 250, 350
speed = 7
x1_speed, y1_speed = speed, speed // 2

rect_width, rect_height = 120, 20
rect_x, rect_y = (width - rect_width) // 2, height - rect_height - 10
rect_speed = 5
rect_width2 = rect_width

lives = 3
end = False
win = False

font = pygame.font.Font(None, 74)
heart_image = pygame.image.load('heart.png')
heart_image = pygame.transform.scale(heart_image, (20, 20))

brick_rows = 5
brick_cols = 9
brick_padding = 5
brick_width = (width - (brick_cols + 1) * brick_padding) // brick_cols
brick_height = 20

b_types = ['life', 'width', 'speed', 'slowdown']
b_falls = []
b_timer = 0
b_active = False
speed_active = False
slow_mode_active = False
speed_timer = 0

def create():
    bricks = []
    for row in range(brick_rows):
        brick_row = []
        for col in range(brick_cols):
            brick_x = col * (brick_width + brick_padding) + brick_padding
            brick_y = row * (brick_height + brick_padding) + brick_padding + 50
            brick = pygame.Rect(brick_x, brick_y, brick_width, brick_height)
            brick_row.append(brick)
        bricks.append(brick_row)
    return bricks

def bonus_bricks(bricks):
    bonuses = []
    bonus_positions = set()
    while len(bonuses) < len(b_types) * 3:
        row = random.randint(0, brick_rows - 1)
        col = random.randint(0, brick_cols - 1)
        position = (row, col)
        if position not in bonus_positions:
            bonus_type = random.choice(b_types)
            bonuses.append({'type': bonus_type, 'position': position})
            bonus_positions.add(position)
    return bonuses

def set_ball_speed(speed, hit_position):
    angle = (hit_position - 0.5) * math.pi / 4
    new_x_speed = speed * math.sin(angle)
    new_y_speed = -speed * math.cos(angle)
    return new_x_speed, new_y_speed

def draw_lives():
    for i in range(lives):
        screen.blit(heart_image, (width - 495 + (i * 30), 10))

def all_bricks_destroyed(bricks):
    return all(all(brick is None for brick in row) for row in bricks)

bricks = create()
bonuses = bonus_bricks(bricks)

done = True
clock = pygame.time.Clock()

while done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = False

    if end:
        game_over_text = font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(game_over_text, (width // 2 - game_over_text.get_width() // 2, height // 2 - game_over_text.get_height() // 2))
    elif win:
        win_text = font.render("YOU WIN", True, (0, 255, 0))
        screen.blit(win_text, (width // 2 - win_text.get_width() // 2, height // 2 - win_text.get_height() // 2))
    else:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            rect_x -= rect_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            rect_x += rect_speed

        if rect_x < 0:
            rect_x = 0
        if rect_x + rect_width > width:
            rect_x = width - rect_width

        x1 += x1_speed
        y1 += y1_speed

        if x1 - r < 0:
            x1 = r
            x1_speed = -x1_speed
        if x1 + r > width:
            x1 = width - r
            x1_speed = -x1_speed
        if y1 - r < 0:
            y1 = r
            y1_speed = -y1_speed

        ball_rect = pygame.Rect(x1 - r, y1 - r, 2 * r, 2 * r)
        rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)

        if ball_rect.colliderect(rect):
            if y1_speed > 0 and y1 + r > rect_y:
                hit_position = (x1 - rect_x) / rect_width
                x1_speed, y1_speed = set_ball_speed(speed, hit_position)
                y1 = rect_y - r

        if y1 + r > height:
            lives -= 1
            if lives <= 0:
                end = True
            else:
                x1, y1 = width // 2, height // 2
                rect_x = (width - rect_width2) // 2
                rect_width = rect_width2

                x1_speed = speed
                y1_speed = speed // 2

                bricks = create()
                bonuses = bonus_bricks(bricks)

        for row_index, row in enumerate(bricks):
            for col_index, brick in enumerate(row):
                if brick and ball_rect.colliderect(brick):
                    row[col_index] = None
                    y1_speed = -y1_speed

                    for bonus in bonuses:
                        if bonus['position'] == (row_index, col_index):
                            bonus_rect = pygame.Rect(brick.x + brick_width // 2 - 10, brick.y + brick_height, 20, 20)
                            b_falls.append({'rect': bonus_rect, 'type': bonus['type']})
                            bonuses.remove(bonus)
                            break
                    break

        if all_bricks_destroyed(bricks):
            win = True

        for bonus in b_falls:
            bonus['rect'].y += 3
            if bonus['rect'].y > height:
                b_falls.remove(bonus)
                continue

            if bonus['rect'].colliderect(rect):
                if bonus['type'] == 'life':
                    lives += 1
                elif bonus['type'] == 'width':
                    b_timer = pygame.time.get_ticks()
                    rect_width = rect_width2 * 2
                elif bonus['type'] == 'speed':
                    speed += 5
                    speed_active = True
                    speed_timer = pygame.time.get_ticks()
                elif bonus['type'] == 'slowdown':
                    speed -= 5
                    slow_mode_active = True
                    speed_timer = pygame.time.get_ticks()
                b_falls.remove(bonus)
            else:
                bonus['rect'].y += 3

        if b_timer and pygame.time.get_ticks() - b_timer > 3000:
            rect_width = rect_width2
            b_timer = 0

        if speed_active and pygame.time.get_ticks() - speed_timer > 3000:
            speed -= 5
            speed_active = False

        if slow_mode_active and pygame.time.get_ticks() - speed_timer > 5000:
            speed += 5
            slow_mode_active = False

        screen.fill((255, 255, 224))
        draw_lives()

        for row_index, row in enumerate(bricks):
            for col_index, brick in enumerate(row):
                if brick:
                    pygame.draw.rect(screen, (0, 128, 255), brick)

        pygame.draw.circle(screen, (255, 20, 147), (x1, y1), r)
        pygame.draw.rect(screen, (32, 178, 170), rect)

        for bonus in b_falls:
            if bonus['type'] == 'life':
                screen.blit(heart_image, bonus['rect'])
            elif bonus['type'] == 'width':
                pygame.draw.circle(screen, (255, 0, 0), (bonus['rect'].centerx, bonus['rect'].centery), 10)
            elif bonus['type'] == 'speed':
                pygame.draw.rect(screen, (165, 42, 42), bonus['rect'])
            elif bonus['type'] == 'slowdown':
                pygame.draw.rect(screen, (255, 165, 0), bonus['rect'])

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
