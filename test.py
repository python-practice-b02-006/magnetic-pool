import pygame
import os


def rotate(surface, angle, pivot, offset):
    """Rotate the surface around the pivot point.

    Args:
        surface (pygame.Surface): The surface that is to be rotated.
        angle (float): Rotate by this angle.
        pivot (tuple, list, pygame.math.Vector2): The pivot point.
        offset (pygame.math.Vector2): This vector is added to the pivot.
    """
    rotated_image = pygame.transform.rotate(surface, -angle)  # Rotate the image.
    rotated_offset = offset.rotate(angle)  # Rotate the offset vector.
    # Add the offset vector to the center/pivot point to shift the rect.
    rect = rotated_image.get_rect(center=pivot+rotated_offset)
    return rotated_image, rect  # Return the rotated image and shifted rect.

def load_image(name, colorkey=None):
    fullname = os.path.join(os.path.dirname(__file__), 'images', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


pygame.init()
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
BG_COLOR = pygame.Color('gray12')
# The original image will never be modified.
IMAGE = load_image("arrow.png", -1)
# pygame.draw.polygon(IMAGE, pygame.Color('dodgerblue3'), ((0, 0), (140, 30), (0, 60)))
# Store the original center position of the surface.
pivot = [200, 250]
# This offset vector will be added to the pivot point, so the
# resulting rect will be blitted at `rect.topleft + offset`.
offset = pygame.math.Vector2(23, 0)
angle = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        angle += 1
    elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
        angle -= 1
    if keys[pygame.K_f]:
        pivot[0] += 2

    # Rotated version of the image and the shifted rect.
    rotated_image, rect = rotate(IMAGE, angle, pivot, offset)

    # Drawing.
    screen.fill(BG_COLOR)
    screen.blit(rotated_image, rect)  # Blit the rotated image.
    pygame.draw.circle(screen, (30, 250, 70), pivot, 3)  # Pivot point.
    pygame.draw.rect(screen, (30, 250, 70), rect, 1)  # The rect.
    pygame.display.set_caption('Angle: {}'.format(angle))
    pygame.display.flip()
    clock.tick(30)