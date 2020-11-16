import math
import pygame

# Also check physics gaming libraries in python

class Vector:
    def __init__(self, mag, th):
        self.magnitude = mag
        self.th = th

    def to_cartesian(self):
        return (math.cos(self.th)*self.magnitude,
                math.sin(self.th)*self.magnitude)

    def from_cartesian(self, cx, cy):
        self.magnitude = math.sqrt(cx*cx + cy**2)
        self.th = math.atan2(cy, cx)

    def from_cartesian_from_screen(self, cx, cy):
        fs_cx, fs_cy = self.from_screen(cx,cy) 
        self.magnitude = math.sqrt(fs_cx*fs_cx + fs_cy**2)
        self.th = math.atan2(fs_cy, fs_cx)

    def __add__(self, other):
        if not isinstance(other, Vector):
            raise Exception("Invalid add type")
        sx, sy = self.to_cartesian()
        ox, oy = other.to_cartesian()
        rx = sx + ox
        ry = sy + oy
        mag = math.sqrt(rx**2 + ry**2)
        th = math.atan2(ry, rx)
        return Vector(mag, th)

    def go_to(self, toV):
        if not isinstance(toV, Vector):
            raise Exception("Invalid add type")
        from_x, from_y = self.to_cartesian()
        to_x, to_y = toV.to_cartesian()
        # print("to_x= {}, to_y = {}".format(to_x,to_y))
        rx = to_x - from_x
        ry = to_y - from_y
        mag = math.sqrt(rx**2 + ry**2)
        th = math.atan2(ry, rx) #+ 0.5 * math.pi
        
        # print("mag= {}, th = {}".format(mag,th))
        return Vector(mag, th)



    def __str__(self):
        return "<{}, {}>".format(self.magnitude, self.th)
    
    def to_screen (self):
        scr_attributes = Screen_attridutes()
        fToScreen = scr_attributes.factor_to_screen
        (x,y) = self.to_cartesian()
        return fToScreen*x, fToScreen*y

    def from_screen (self, cx, cy ):        
        scr_attributes = Screen_attridutes()
        fToScreen = scr_attributes.factor_to_screen
        return cx/fToScreen, cy/fToScreen
    
class PhysicsObject:
    def __init__(self, r = Vector(0, 0), u = Vector(0, 0)):
        self.r = r
        self.u = u

    def apply_force(self, f, dt):
        fx, fy = f.to_cartesian()
        ux, uy = self.u.to_cartesian()

        ux = ux + fx * dt
        uy = uy + fy * dt

        x, y = self.r.to_cartesian()
        
        x = x + ux*dt
        y = y + uy*dt
        
        self.u.from_cartesian(ux, uy)
        self.r.from_cartesian(x, y)
    
    def __str__(self):
        return "[r = {}, u={}]".format(self.r, self.u)


# 
class PaintableObject:
    def __init__(self, physobj, sprite):
        pass


class Enemy:
    def __init__(self, position):
        new_rV = Vector(0.0, 0.0)
        new_rV.from_cartesian_from_screen(position[0],position[1])
        new_uV = Vector(2, 0.0) # 2 m/s
        
        self.r_and_u = PhysicsObject(new_rV, new_uV)
        self.radius = 0.3125
        
        self.colour =  [  (255, 214, 214), (240, 175, 175), (255, 184, 184), 
        (255, 138, 138),(255, 84, 84), (222, 73, 73), (255, 54, 54),  (219, 9, 9), (194, 31, 31), (163, 7, 7)]
        
        self.thickness = 5
        
        self.p = -1
        self.health = 9 # if changed then the colour list must be extended as well

   
    def display(self, screen):
        (x,y) = self.r_and_u.r.to_screen()
        scr_attributes = Screen_attridutes()
        to_sc = scr_attributes.factor_to_screen
        pygame.draw.circle(screen, self.colour[self.health], (int(x), int(y)), int(self.radius*to_sc), self.thickness)
        # pygame.draw.circle(screen, self.colour, (int(x), int(y)), int(self.radius*to_sc), self.thickness)
       
   
    def route(self):
        scr_attributes = Screen_attridutes()
        p = self.p
        dy_in_route= scr_attributes.dy_in_route  #metres
        enemy_size_offset = self.radius #/ scr_attributes.factor_to_screen  #metres

        # p metres
        if p<0 :
            p = 0
            return (0, 0)

        count_inner_set =0
        offset=0
        offset_standard = scr_attributes.width_meters #screenX_metres
        previous_height = -dy_in_route
        new_x_metres=0.0
        new_y_metres=0.0
        for check in scr_attributes.check_points:            
            if( check - offset == offset_standard): #left or right
                previous_height += dy_in_route
            #print("p= {}, check={}, offset={}, previous_height={}, count_inner_set={}"
            # .format(p, check, offset, previous_height, count_inner_set))
            if (p>=offset and p<check):
                #print("p>offset and p<check")
                if count_inner_set ==0: #going right(->) -.
                    new_x_metres = p-offset
                    new_y_metres = previous_height
                    if new_y_metres == 0:
                        new_y_metres +=enemy_size_offset
                    elif new_y_metres == scr_attributes.height_meters:
                        new_y_metres -=enemy_size_offset 
                elif count_inner_set ==1: #going down from right(|) |.
                    new_x_metres = offset_standard - enemy_size_offset
                    new_y_metres = previous_height + (p - offset)
                elif count_inner_set ==2: #going left(<-) .-
                    new_x_metres = offset_standard - (p-offset)
                    new_y_metres = previous_height               
                elif count_inner_set ==3: #going down from left(|) .|
                    new_x_metres = 0 + enemy_size_offset
                    new_y_metres = previous_height + (p - offset)
                   
                # print("route v:<{},{}>".format(new_x_metres, new_y_metres))
                (x,y) =self.r_and_u.r.to_cartesian()
                dx = new_x_metres - x 
                dy = new_y_metres - y
                self.r_and_u.r.from_cartesian(new_x_metres, new_y_metres)
                self.r_and_u.u.th =math.atan2(dy, dx)

                # print(self.r_and_u.__str__())
                # (nnx,nny) = self.r_and_u.r.to_cartesian()
                # print("route v r.to_cartesian:<{},{}>".format(nnx, nny))
                            
            count_inner_set +=1
            if count_inner_set ==4:
                count_inner_set =0
            offset = check         
    
  
    def to_screen(self, x, y, factor_to_screen):
        self.x = factor_to_screen*x
        self.y = factor_to_screen*y

    
    def is_hit (self, b ):
        (ex,ey) = self.r_and_u.r.to_cartesian()   
        (bx,by) = b.r_and_u.r.to_cartesian() 
        #distance between center of enemy and bullet point left up
        #distance between center of enemy and bullet point left down
        #distance between center of enemy and bullet point right up
        #distance between center of enemy and bullet point right down
        return (math.sqrt( (ex - bx)**2 + (ey - by)**2 ) < self.radius 
                or math.sqrt( (ex - bx)**2 + (ey - (by + b.r_height))**2 ) < self.radius
                or math.sqrt( (ex - (bx + b.r_width))**2 + (ey - by)**2 ) < self.radius
                or math.sqrt( (ex - (bx + b.r_width))**2 + (ey - (by + b.r_height))**2 ) < self.radius )
     
    def subtrack_health(self):
        self.health -= 1

    def find_two_closest_bullets(self, t ):
        d_close = 5
        two_closest_bullets = [] # size 2, bullet-distance. Closest bullet is in [0], second closest in [1]
        (xe, ye) = self.r_and_u.r.to_cartesian()

        first_closest_bullet = None
        fcb_d = 5.1
        second_closest_bullet = None
        scb_d = 5.1
        for b in t.bullets:
            (xb, yb) = b.r_and_u.r.to_cartesian()
            d = math.sqrt( (xe-xb)**2 + (ye-yb)**2 )
            # print("{}. enemy = [{}, {}] bullet= [{}, {}], distance={}".format(count, xe, ye, xb, yb, d))
            if (d <= d_close):
                if (d < fcb_d):
                    second_closest_bullet = first_closest_bullet
                    scb_d = fcb_d
                    first_closest_bullet = b
                    fcb_d = d
                    # (xb, yb) = first_closest_bullet.r_and_u.r.to_cartesian()            
                    # print("Firsrt bullet= [{}, {}], distance={}".format(xb, yb, fcb_d))
                    # if (second_closest_bullet is not None):
                    #     (xb, yb) = second_closest_bullet.r_and_u.r.to_cartesian()            
                        # print("second bullet= [{}, {}], distance={}".format(xb, yb, scb_d))

                elif d < scb_d and d is not fcb_d:
                    second_closest_bullet = b
                    scb_d = d
                    # (xb, yb) = second_closest_bullet.r_and_u.r.to_cartesian()            
                    # print("second bullet= [{}, {}], distance={}".format(xb, yb, scb_d))
               
        if (first_closest_bullet is not None):
            two_closest_bullets.append(first_closest_bullet)             
        if (second_closest_bullet is not None):
            two_closest_bullets.append(second_closest_bullet)
        
        return two_closest_bullets
        
       



class Screen_attridutes:
    def __init__(self):
        self.background_colour = (119,136,153) 
        (self.width, self.height) = (800, 640)
        self.width_meters = 50.0
        self.height_meters = self.width_meters * self.height / self.width
        self.max_loop_sets = 5
        self.h_in_set = 2
        self.dy_in_route = self.height_meters/ (self.max_loop_sets*self.h_in_set)
        self.MAX_DIST = (self.width_meters + self.dy_in_route) * self.h_in_set * self.max_loop_sets + self.width_meters
        self.factor_to_screen = self.width//self.width_meters
        self.check_points = self.calculate_checkpoints()
        self.x_y_checkpoints = self.calculate_x_y_checkpoints()
        # self.screen_checkpoints = self.checpoints_to_screen()

     
    def calculate_checkpoints(self):        
        dy = self.dy_in_route
        dx = self.width_meters
        
        check_points=[]
        for i in range(self.max_loop_sets*2):
            check_points.append((i+1)*dx +i*dy)
            check_points.append((i+1)*dx +(i+1)*dy)
        check_points.append((self.max_loop_sets*2+1)*dx +self.max_loop_sets*2*dy)
        
        return check_points
    
    def calculate_x_y_checkpoints(self):
        dy = self.dy_in_route
        dx = self.width_meters
        check_points = []
        x = 0 
        y = -dy
        
        for i in range(self.max_loop_sets):
            for i in range(4):
                if i%2==0: #going down
                    y+=dy
                elif i == 1:#goint right
                    x +=dx
                else:
                    x -=dx
               
                v= Vector(0,0)
                v.from_cartesian(x,y)
                check_points.append(v)
        y+=dy
        v= Vector(0,0)
        v.from_cartesian(x,y)
        check_points.append(v)
        # print("xs = {}, ys = {} ".format( x,y)) 
        x +=dx        
        v= Vector(0,0)
        v.from_cartesian(x,y)
        check_points.append(v)
        # print("xs = {}, ys = {} ".format( x,y)) 
        return check_points

    # def checpoints_to_screen(self):
    #     metre_checkpoint = self.x_y_checkpoints        
    #     screen_check_points = []
       
    #     for v in metre_checkpoint:
    #         (x,y) = v.to_screen()
    #         screen_check_points.append((x,y) )
    #     return screen_check_points

    
    def display_route(self, screen):
        color = (131, 148, 166)
        metre_checkpoint = self.x_y_checkpoints        
        screen_check_points = []
        for v in metre_checkpoint:
            (x,y) = v.to_screen()
            # (xc,yc) = v.to_cartesian()
            screen_check_points.append((x,y) )
            # print("xs = {}, ys = {} | xm = {}, ym = {}".format( x,y,xc,yc))

         
        pygame.draw.lines(screen, color, False, screen_check_points, 6 )


    def is_tower_possition_allowed_simple(self, tower):
        (xt, yt) = tower.r.to_cartesian()
        yt = yt  - tower.symmetrical_distance #( the middle of total height of triangle)
        dmin = 2* tower.symmetrical_distance
        dy = self.dy_in_route
        print("xt = {} yt = {}. dmin = {} ".format( xt, yt,dmin))
            
        remainder = yt % dy
        
        if  remainder < dmin  or  dy - remainder < dmin  :
            return False
        elif xt < dmin or xt > self.width_meters - dmin:
            return False
        else: return True


    def is_tower_possition_allowed(self, tower):
        
        (xt, yt) = tower.r.to_cartesian()
        yt = yt  - tower.symmetrical_distance #( the middle of total height of triangle)
        dmin = 2 * tower.symmetrical_distance
        x0e = 0
        y0e = 0
        e = Enemy((0, 0))
        ue = e.r_and_u.u.magnitude
       
        k = 0
        previous_distance = 100
        print("is_tower_possition_allowed")
        while k<50:
                 
            const_a = - 2 * (yt - y0e) * ue 
            const_b = 2 * (xt - x0e) * ue
            const_c = math.atan2(const_a,const_b)
            const_d = 1 / ( 2 * ue**2)

            print("is_tower_possition_allowed k= {}".format(k))

            th = k * math.pi - const_c
            print("is_tower_possition_allowed th= {}".format(th))
            
            t = const_d * (const_a * math.sin(th) - const_b * math.cos(th))
            print("is_tower_possition_allowed t= {}".format(t))
            x = x0e + ue * math.cos(th) * t
            y = y0e + ue * math.sin(th) * t
            dx = xt - x0e - ue * math.cos(th) * t
            dy = yt - y0e - ue * math.sin(th) * t
            print("x= {}, y = {}, xt = {} yt = {}. dx = {} , dy = {}".format(x,y, xt, yt, dx,dy))
            
            d = math.sqrt( dx**2 + dy**2)
            
            print("is_tower_possition_allowed d= {}, dmin = {}, previous_d = {}".format(d,dmin,previous_distance))
            if d < dmin:
                return False
            elif previous_distance < d:
                return True
            elif previous_distance>d:
                previous_distance = d
                x0e += ue * math.cos(th) * t
                y0e += ue * math.sin(th) * t
            
            k +=1
            
        print("is_tower_possition_allowed end")
        





class Tower:
    def __init__(self, position):
        rV = Vector(0.0, 0.0)
        rV.from_cartesian_from_screen(position[0],position[1])
        self.r = rV
        # self.x = position[0]
        # self.y = position[1]
        self.colour = (204,153,0)
        self.symmetrical_distance = 0.625
        self.bullets = []
        self.max_bullets = 10
        
   
    def display(self, screen):
        (x,y) = self.r.to_screen()
        symmetrical_distance_toScreen  = self.symmetrical_distance * Screen_attridutes().factor_to_screen
        pointlist_3 = [(x - symmetrical_distance_toScreen, y), (x + symmetrical_distance_toScreen, y), (x, y - 2*symmetrical_distance_toScreen)]
        pygame.draw.polygon(screen, self.colour, pointlist_3, 0)
        # pointlist_3 = [(self.x - self.symmetrical_distance, self.y), (self.x + self.symmetrical_distance, self.y), (self.x, self.y - 2*self.symmetrical_distance)]
        # pygame.draw.polygon(screen, self.colour, pointlist_3, 0)

    def make_bullet(self, to_x, to_y):
        toV = Vector(0.0, 0.0)
        toV.from_cartesian_from_screen(to_x,to_y)
        if len(self.bullets) < self.max_bullets:
            self.bullets.append(Bullet(self.r, toV))#, (self.x, self.y- self.symmetrical_distance), (to_x, to_y)))

class Observer_tower:
    def __init__(self, position):
        rV = Vector(0.0, 0.0)
        rV.from_cartesian_from_screen(position[0],position[1])
        # (x,y) =rV.to_cartesian()
        #print("OBSERVER tower: x= {}, y = {}".format(x,y))
        self.r = rV

        # self.x = position[0]
        # self.y = position[1]

        self.colour =(44, 0, 176) # (209, 92, 2)#(204, 105, 0) # (240,143,16)
        self.symmetrical_distance =  0.625
        self.bullets = []
        self.max_bullets = 10
        
   
    def display(self, screen):
        (x,y) = self.r.to_screen()
        symmetrical_distance_toScreen  = self.symmetrical_distance * Screen_attridutes().factor_to_screen
        pointlist_3 = [(x - symmetrical_distance_toScreen, y), (x + symmetrical_distance_toScreen, y), (x, y - 2*symmetrical_distance_toScreen)]
        pygame.draw.polygon(screen, self.colour, pointlist_3, 0)

    def make_bullet(self, e ):
        #print (len(self.bullets)  )
        #print (self.max_bullets  )


        if len(self.bullets) < self.max_bullets:  
            #(x,y) = self.r.to_cartesian()
            b = Bullet(self.r, Vector(0,0))
            (xt,yt) = self.r.to_cartesian()
            ub = b.r_and_u.u.magnitude
            # print ("NEW bullet before calculations: th = {} ".format( b.r_and_u.u.th ))
            # (x,y) = b.r_and_u.r.to_cartesian()
            # print(" NEW bullet before calculations x= {}, y = {}".format(x,y))

            (xe,ye) = e.r_and_u.r.to_cartesian()
            (uxe,uye) = e.r_and_u.u.to_cartesian()
            
            # print(" NEW bullet enemy: uxe= {}, uye = {}".format(uxe,uye))
            # print(e.r_and_u.__str__())

            # after solving the motion equations of e,b
            #  to find the collision point/ angle of speed of the bullet, as e, b: eythygrammi omali kinisi
            # (yt - ye) * uxe - (xt - xe) * uye = (yt - ye) * ub * cos(th) - (xt - xe) * ub * sin(th)
            # (yt - ye) * uxe - (xt - xe) * uye - (yt - ye) * ub * cos(th) + (xt - xe) * ub * sin(th) = 0
            # A -B cos(th) - C sin(th) = 0
            # A - sqrt(B^2 +C^2) * sin (th + arctan(B/C)) = 0
            # th = arcsin(A/D) - E  

            const_a = (yt - ye) * uxe - (xt - xe) * uye
            const_b = (yt - ye) * ub
            const_c = -(xt - xe) * ub

            const_d = math.sqrt (const_b**2 + const_c**2)
            const_e = math.atan2(const_b,const_c)

            th = math.asin(const_a/const_d) - const_e

            b.r_and_u.u.th = th 
            # print ("NEW bullet: th = {} ".format( b.r_and_u.u.th ))
            # (x,y) = b.r_and_u.r.to_cartesian()
            # print(" NEW bullet x= {}, y = {}".format(x,y))
            # print(b.r_and_u.__str__())

            self.bullets.append(b)
     

        

class Bullet:
    def __init__(self, fromV,toV):# ,position, to):  
        r = fromV.go_to(toV)
        v = Vector(8,r.th)
        # print(r.__str__())
        
        # (x,y) =r.to_cartesian()
        # print("x= {}, y = {}".format(x,y))
        self.r_and_u = PhysicsObject(Vector(fromV.magnitude,fromV.th), v)

        # self.x = position[0]
        # self.y = position[1]
        # self.angle = math.atan2( to[1]- self.y, to[0]-self.x)+ 0.5 * math.pi

        self.r_width = 0.3125
        self.r_height = 0.3125
        self.colour = (71, 70, 57)#(1,1,3)
        self.thickness = 15
        # th = math.atan2(self.x, self.y)
        # self.p_o = PhysicsObject(Vector(math.sqrt(self.x**2 + self.y**2), th), Vector(self.u_magnitude, th))
    
    def display(self, screen):
        (x,y) = self.r_and_u.r.to_screen()
        scr_attributes = Screen_attridutes()
        to_sc = scr_attributes.factor_to_screen
        pygame.draw.rect(screen, self.colour, pygame.Rect((x, y, int(self.r_width * to_sc), int (self.r_height *to_sc))), 0)

    def move(self,dt):
        self.r_and_u.apply_force(Vector(0,0),dt)
        # print("MOVE bullet")
        # print(self.r_and_u.__str__())
        # (x,y) = self.r_and_u.r.to_cartesian()
        # print("MOVE bullet x= {}, y = {}".format(x,y))
        

    def is_in_screen (self):
        #upper screen limit
        scr_attributes = Screen_attridutes()
        (x,y) = self.r_and_u.r.to_cartesian()
        return (y + self.r_height >0
                and y < scr_attributes.height_meters
                and x < scr_attributes.width_meters
                and x + self.r_width >0)

        # return (self.y + self.r_height >0
        #         and self.y < mscr_attributesyscreen.height
        #         and self.x < scr_attributes.width
        #         and self.x + self.r_width >0)



