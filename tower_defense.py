import math
import random
import pygame
import entities

myscreen = entities.Screen_attridutes()
RIGHT = 3
LEFT  = 1

screen = pygame.display.set_mode((myscreen.width, myscreen.height),pygame.DOUBLEBUF)
pygame.display.set_caption('Tower Defence')

#adding a comment to check git commit
running = True
enemies = []   

# my_second_enemy =  entities.Enemy((150, 150))
# enemies.append(my_second_enemy)

clock=pygame.time.Clock()
FRAMES_PER_SECOND=30
user_tower_exists = False
observer_tower_exists = False
user_bullet_exists = False
while running:  
    dt=clock.tick(FRAMES_PER_SECOND)/1000.0 # number of seconds have passed since the previous call.
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False            
        elif event.type == pygame.MOUSEBUTTONUP and event.button == RIGHT and not observer_tower_exists:
            pos = pygame.mouse.get_pos()
            observer_tower = entities.Observer_tower(pos)     
            if (myscreen.is_tower_possition_allowed_simple(observer_tower)):
                observer_tower_exists = True
            else:
                print("tower is not allowed at x= {}, y = {}".format(pos[0], pos[1]))
                del observer_tower
        elif event.type == pygame.MOUSEBUTTONUP and not user_tower_exists:
            pos = pygame.mouse.get_pos()
            tower = entities.Tower(pos)
            if (myscreen.is_tower_possition_allowed_simple(tower)):
                user_tower_exists = True
            else:
                print("tower is not allowed at x= {}, y = {}".format(pos[0], pos[1]))
                del tower
        elif event.type == pygame.MOUSEBUTTONUP and  user_tower_exists:
            (x,y) = pygame.mouse.get_pos()
            tower.make_bullet(x,y)
            user_bullet_exists = True

   
    #bullet = entities.Bullet((40,50))

    if random.random() < 0.05 and len(enemies) < 50:
        enemies.append(entities.Enemy((0, 0)))

    new_enemies = []
    two_closest_bullets = []
    for e in enemies:
        e.p += e.r_and_u.u.magnitude *dt
        if e.p > myscreen.MAX_DIST:
            del e
        else:
            new_enemies.append(e)        
            e.route( )#myscreen.check_points, myscreen.height_down, myscreen.width_meters, myscreen.height_meters, myscreen.factor_to_screen)
            if(observer_tower_exists):
                two_closest_bullets = e.find_two_closest_bullets(observer_tower)

            if random.random() < 0.05 and observer_tower_exists and len(observer_tower.bullets) <observer_tower.max_bullets:
                observer_tower.make_bullet(e)
    enemies = new_enemies
    # my_second_enemy.p += e.r_and_u.u.magnitude * dt
    # if my_second_enemy.p > myscreen.MAX_DIST:
    #     my_second_enemy.p = 0
    # my_second_enemy.route1( )#myscreen.check_points, myscreen.height_down, myscreen.width_meters, myscreen.height_meters, myscreen.factor_to_screen)
    
    new_bullets = []
    hit_bullets = []
    if user_bullet_exists:
        for b in tower.bullets:
            b.move(dt)
            if b.is_in_screen():
                new_bullets.append(b)

        bullets = new_bullets
        for b in tower.bullets:
            for e in enemies:
                if e.is_hit(b) and not b in hit_bullets:
                    e.subtrack_health()
                    if (e.health<0):
                        enemies.remove(e)
                        del e
                    hit_bullets.append(b)
        
        for b in hit_bullets:
            if b in new_bullets:
                new_bullets.remove(b)
                del b

        tower.bullets = new_bullets

            
    new_bullets = []
    hit_bullets = []
    if observer_tower_exists:
        for b in observer_tower.bullets:
            b.move(dt)
            if b.is_in_screen():
                new_bullets.append(b)

        bullets = new_bullets
        for b in bullets:
            for e in enemies:
                if e.is_hit(b) and not b in hit_bullets:
                    e.subtrack_health()
                    if (e.health<0):
                        enemies.remove(e)
                        del e
                    hit_bullets.append(b)
        
        for b in hit_bullets:
            if b in new_bullets:
                new_bullets.remove(b)
                del b

        observer_tower.bullets = new_bullets

           


    ## PLOT
    screen.fill( myscreen.background_colour)
    myscreen.display_route(screen)    
    # my_second_enemy.display1(screen)
    if user_tower_exists:
        tower.display(screen)
    #if user_bullet_exists:
        for b in tower.bullets:
            b.display(screen)

    if observer_tower_exists:
        observer_tower.display(screen)
        for b in observer_tower.bullets:
            b.display(screen)

    for e in enemies:
        e.display(screen)
    pygame.display.flip()



  

pygame.quit()

