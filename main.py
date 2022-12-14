
import pygame
import os
import math
import sys
import neat
import csv

SCREEN_WIDTH = 2560
SCREEN_HEIGHT = 1016
glass_color = (2, 105, 31, 255)
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Drive AI")

TRACK = pygame.image.load(os.path.join("Assets", "track.png"))


class Car(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = pygame.image.load(
            os.path.join("Assets", "car.png"))
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(490, 820))
        # self.drive_state = False
        self.vel_vector = pygame.math.Vector2(0.8, 0)
        self.angle = 0
        self.rotation_vel = 5
        self.direction = 0
        self.alive = True
        self.radars = []
        self.counter = 0
        self.vector_num = 0

    def update(self):
        self.radars.clear()
        self.drive()
        self.rotate()
        for radar_angle in (-60, -30, 0, 30, 60):
            self.radar(radar_angle)
        self.collision()
        self.data()

    def drive(self):
        # if self.drive_state:
        self.rect.center += self.vel_vector * self.vector_num

    def collision(self):
        length = 40
        collision_point_right = [int(self.rect.center[0] + math.cos(math.radians(self.angle + 18)) * length),
                                 int(self.rect.center[1] - math.sin(math.radians(self.angle + 18)) * length)]
        collision_point_left = [int(self.rect.center[0] + math.cos(math.radians(self.angle - 18)) * length),
                                int(self.rect.center[1] - math.sin(math.radians(self.angle - 18)) * length)]

        # Die on Collision
        if SCREEN.get_at(collision_point_right) == pygame.Color(2, 105, 31, 255) \
                or SCREEN.get_at(collision_point_left) == pygame.Color(2, 105, 31, 255):
            self.alive = False

        # Draw Collision Points
        pygame.draw.circle(SCREEN, (0, 255, 255, 0), collision_point_right, 4)
        pygame.draw.circle(SCREEN, (0, 255, 255, 0), collision_point_left, 4)

    def rotate(self):
        if self.direction == 1:
            self.angle -= self.rotation_vel
            self.vel_vector.rotate_ip(self.rotation_vel)

        if self.direction == -1:
            self.angle += self.rotation_vel
            self.vel_vector.rotate_ip(-self.rotation_vel)

        self.image = pygame.transform.rotozoom(
            self.original_image, self.angle, 0.1)
        self.rect = self.image.get_rect(center=self.rect.center)

    def radar(self, radar_angle):
        length = 0
        x = int(self.rect.center[0])
        y = int(self.rect.center[1])

        while not SCREEN.get_at((x, y)) == pygame.Color(glass_color) and length < 200:
            length += 1
            x = int(self.rect.center[0] +
                    math.cos(math.radians(self.angle + radar_angle)) * length)
            y = int(self.rect.center[1] -
                    math.sin(math.radians(self.angle + radar_angle)) * length)

        pygame.draw.line(SCREEN, (255, 255, 255, 255),
                         self.rect.center, (x, y), 1)
        pygame.draw.circle(SCREEN, (0, 255, 0, 0), (x, y), 3)

        dist = int(math.sqrt(
            math.pow(self.rect.center[0] - x, 2)+math.pow(self.rect.center[1] - y, 2)))

        self.radars.append([radar_angle, dist])

    def data(self):
        input = [0, 0, 0, 0, 0]
        for i, radar in enumerate(self.radars):
            input[i] = int(radar[1])
        return input

    def life(self):
        self.counter += 1
        if self.counter == 10000:
            self.alive = False


def remove(index):
    cars.pop(index)
    ge.pop(index)
    nets.pop(index)


# car = pygame.sprite.GroupSingle(Car())


def eval_genomes(genomes, config):
    global cars, ge, nets

    cars = []
    ge = []
    nets = []

    for genome_id, genome in genomes:
        cars.append(pygame.sprite.GroupSingle(Car()))
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    run = True
    while run:
        f = open('./output.csv', 'a')
        f2 = open('./input.csv', 'a')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                f.close()
                pygame.quit()
                sys.exit()

        SCREEN.blit(TRACK, (0, 0))

        if len(cars) == 0:
            break

        for i, car in enumerate(cars):
            car.sprite.life()
            ge[i].fitness += 1
            if not car.sprite.alive:
                remove(i)

        for i, car in enumerate(cars):
            # writer = csv.writer(f2)
            # writer.writerow(car.sprite.data())

            output = nets[i].activate(car.sprite.data())

            # writer = csv.writer(f)
            # writer.writerow(output)

            # print(output[2])
            car.sprite.vector_num = 6
            # car.sprite.vector_num = output[2] *20

            # if output[0] <= 0.7 and output[1] <= 0.7:
            #     car.sprite.vector_num = 15
            # if output[0] <= 0.6 and output[1] <= 0.6:
            #     car.sprite.vector_num = 10
            # if output[0] <= 0.5 and output[1] <= 0.5:
            #     car.sprite.vector_num = 9
            # if output[0] <= 0.4 and output[1] <= 0.4:
            #     car.sprite.vector_num = 8
            # if output[0] <= 0.3 and output[1] <= 0.3:
            #     car.sprite.vector_num = 7

            if output[0] > 0.7:
                car.sprite.direction = 1
            if output[1] > 0.7:
                car.sprite.direction = -1
            if output[0] <= 0.7 and output[1] <= 0.7:
                car.sprite.direction = 0
                car.sprite.vector_num = 15

        # user_input = pygame.key.get_pressed()
        # if sum(pygame.key.get_pressed()) <= 1:
        #     car.sprite.drive_state = False
        #     car.sprite.direction = 0

        # if user_input[pygame.K_SPACE]:
        #     car.sprite.drive_state = True

        # if user_input[pygame.K_RIGHT]:
        #     car.sprite.direction = 1

        # if user_input[pygame.K_LEFT]:
        #     car.sprite.direction = -1
        for car in cars:
            car.draw(SCREEN)
            car.update()

        pygame.display.update()


# eval_genomes()

def run(config_path):
    global pop
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    pop = neat.Population(config)

    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    pop.run(eval_genomes, 50)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)
