import math
import random
import pygame
import entities
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

myscreen = entities.Screen_attridutes()
RIGHT = 3
LEFT  = 1

screen = pygame.display.set_mode((myscreen.width, myscreen.height),pygame.DOUBLEBUF)
pygame.display.set_caption('Tower Defence')



############################################# A2C ###############################################
###############################################
#A2C: setting up the nn networks and parametres
random.seed(42)
gamma = 0.99  # Discount factor for past rewards
max_steps_per_episode = 100
eps = np.finfo(np.float32).eps.item()  # Smallest number such that 1.0 + eps != 1.0

# actor critic network 
num_inputs = 1 + (2 + 2) + (2 + 2)
#going forward or backward in the path.
# 0 : going forward
# 1 : going backwards
num_actions = 2 
num_hidden = 32

inputs = layers.Input(shape=(num_inputs,))
common = layers.Dense(num_hidden, activation="relu")(inputs)
action = layers.Dense(num_actions, activation="softmax")(common)
critic = layers.Dense(1)(common)

model = keras.Model(inputs=inputs, outputs=[action, critic])
###############################################


class eBrain:
    def __init__(self, enemy,trainable ):
        self.optimizer = keras.optimizers.Adam(learning_rate=0.01)
        self.huber_loss = keras.losses.Huber()
        self.action_probs_history = []
        self.critic_value_history = []
        self.rewards_history = []
        self.running_reward = 0
        self.episode_count = 0
        self.me_the_enemy = enemy
        self.trainable = trainable
        self.to_be_deleted = False
        self.step_reward = 0

    def take_an_action (self, tc_bullets):

         # SLOPPY (start)
        bstates = []
        bcnt = 0
        for b in tc_bullets:
            bstates = bstates + b.to_state_vector()
            bcnt = bcnt + 1

        while bcnt < 2:
            bstates = bstates + [0, 0, 0, 0]
            bcnt = bcnt + 1
        # SLOPPY (end)

        # reset the environment
        state = [self.me_the_enemy.p] + bstates
        #print("STATE IS", state)
        
        state = tf.convert_to_tensor(state)
        state = tf.expand_dims(state, 0)

        # Predict action probabilities and estimated future rewards
        # from environment state
        action_probs, critic_value = model(state)
        if self.trainable:
            self.critic_value_history.append(critic_value[0, 0])

        # Sample action from action probability distribution
        action = np.random.choice(num_actions, p=np.squeeze(action_probs))
        if self.trainable:
            self.action_probs_history.append(tf.math.log(action_probs[0, action]))
        
        return action
   
       
    def learn(self, episode_reward):
        if not self.trainable:
            return
        print("learn CALLED")
        # Update running reward to check condition for solving
        self.running_reward = 0.05 * episode_reward + (1 - 0.05) * self.running_reward

        # Calculate expected value from rewards
        # - At each timestep what was the total reward received after that timestep
        # - Rewards in the past are discounted by multiplying them with gamma
        # - These are the labels for our critic
        returns = []
        discounted_sum = 0
        for r in self.rewards_history[::-1]:
            discounted_sum = r + gamma * discounted_sum
            returns.insert(0, discounted_sum)

        # Normalize
        returns = np.array(returns)
        returns = (returns - np.mean(returns)) / (np.std(returns) + eps)
        returns = returns.tolist()

        # Calculating loss values to update our network
        history = zip(self.action_probs_history, self.critic_value_history, returns)
        actor_losses = []
        critic_losses = []
        for log_prob, value, ret in history:
            # At this point in history, the critic estimated that we would get a
            # total reward = `value` in the future. We took an action with log probability
            # of `log_prob` and ended up recieving a total reward = `ret`.
            # The actor must be updated so that it predicts an action that leads to
            # high rewards (compared to critic's estimate) with high probability.
            diff = ret - value
            actor_losses.append(-log_prob * diff)  # actor loss

            # The critic must be updated so that it predicts a better estimate of
            # the future rewards.
            critic_losses.append(
                self.huber_loss(tf.expand_dims(value, 0), tf.expand_dims(ret, 0))
            )

        # Backpropagation
        loss_value = sum(actor_losses) + sum(critic_losses)
        grads = tape.gradient(loss_value, model.trainable_variables)
        print (grads)
        self.optimizer.apply_gradients(zip(grads, model.trainable_variables))

        # Clear the loss and reward history
        self.action_probs_history.clear()
        self.critic_value_history.clear()
        self.rewards_history.clear()

###############################################

##############################################################################################



def append_enemies (smart_enemies, trainable_enemy_exists):
    
    trainable = False
    if random.random() < 0.5 and len(smart_enemies) < max_enemies:
        e = entities.Enemy((0, 0))

        # first enemy is trainable or there is no trainable agent
        if not trainable_enemy_exists :
            trainable = True
            
        
        print("ADD NEW ENEMY trainable_enemy_exists= {}".format(trainable_enemy_exists))
        smart_enemies.append( eBrain(e,trainable) )
    return trainable or trainable_enemy_exists
        
def __del__ (self):
    pass

def active_bullets_after_collision_checks (tower, smart_enemies, episode_reward, steps_count):
    new_bullets = []
    hit_bullets = []
    for b in tower.bullets:
        b.move(dt)
        if b.is_in_screen():
            new_bullets.append(b)

    # the first enemy is always trainable
    trainable_enemy_exists = True
    for b in tower.bullets:
        for eb in smart_enemies:
            e = eb.me_the_enemy
            if e.is_hit(b) and not b in hit_bullets:
                e.subtrack_health()
                eb.step_reward += penalty_hit
                if (e.health<0):
                    if eb.trainable:                          
                        eb.step_reward += penalty_death
                        
                        ed.rewards_history.append(ed.step_reward)
                        episode_reward += ed.step_reward
                        print("learn CALLING")
                        eb.learn(episode_reward)
                        trainable_enemy_exists = False 
                        episode_reward = 0
                        steps_count = 0
                        eb.trainable = False
                    smart_enemies.remove(eb)
                    #del eb
                hit_bullets.append(b)
    
    for b in hit_bullets:
        if b in new_bullets:
            new_bullets.remove(b)
            #del b

    return new_bullets, trainable_enemy_exists , episode_reward, steps_count



running = True
enemies = []   
smart_enemies = []   
clock=pygame.time.Clock()
FRAMES_PER_SECOND=30
stopwatch_at = 2 #secs
stopwatch_timer = 0
stopwatcht_at_bullet = 1 #sec
stopwatch_timer_bullet = 0
max_enemies = 1

reward_reach_the_castle = 100
reward_moving_forward = 0.1
reward_moving_backwards = 0
penalty_hit = -50
penalty_death = -10

observer_towers = []
user_towers = []


trainable_enemy_exists = False

episode_reward = 0
steps_count  = 0

while running:  
    
    with tf.GradientTape() as tape:
            # env.render(); Adding this line would show the attempts
            # of the agent in a pop up window.
            
            dt=clock.tick(FRAMES_PER_SECOND)/1000.0 # number of seconds have passed since the previous call.
            stopwatch_timer += dt
            stopwatch_timer_bullet += dt
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False            
                elif event.type == pygame.MOUSEBUTTONUP and event.button == RIGHT and not observer_towers:
                    pos = pygame.mouse.get_pos()
                    observer_tower = entities.Observer_tower(pos)     
                    if (myscreen.is_tower_possition_allowed_simple(observer_tower)):
                        observer_towers.append(observer_tower)
                    else:
                        # print("tower is not allowed at x= {}, y = {}".format(pos[0], pos[1]))
                        #del observer_tower
                        pass
                elif event.type == pygame.MOUSEBUTTONUP and not user_towers:
                    pos = pygame.mouse.get_pos()
                    tower = entities.Tower(pos)
                    if (myscreen.is_tower_possition_allowed_simple(tower)):
                        user_towers.append(tower)
                    else:
                        # print("tower is not allowed at x= {}, y = {}".format(pos[0], pos[1]))
                        #del tower
                        pass
                elif event.type == pygame.MOUSEBUTTONUP and  user_towers:
                    (x,y) = pygame.mouse.get_pos()
                    tower.make_bullet(x,y)

            #add a smart agent
            if stopwatch_timer >= stopwatch_at:
                trainable_enemy_exists = append_enemies(smart_enemies, trainable_enemy_exists)
                
                # print("trainable_enemy_exists= {}".format(trainable_enemy_exists))
                stopwatch_timer = 0

            new_smart_enemies = []
            two_closest_bullets = []
            for eb in smart_enemies:
                e = eb.me_the_enemy
                tc_bullets = []
                #find needs modification to find closet bullets from all towers
                for ot in observer_towers:
                        tc_bullets = e.find_two_closest_bullets(ot)

                action = eb.take_an_action(tc_bullets)

                e.p += ((-1)** action) * e.r_and_u.u.magnitude *dt
                print("action= {}, p = {}".format(action, e.p))

                if e.p >= myscreen.MAX_DIST:
                    eb.step_reward += reward_reach_the_castle                    
                    if eb.trainable: 
                        trainable_enemy_exists = False 
                        eb.learn(episode_reward)
                    #del eb
                else:
                    new_smart_enemies.append(eb)        
                    e.route( )
                    if action == 0 :
                        eb.step_reward += reward_moving_forward
                    else:
                        eb.step_reward += reward_moving_backwards

                    print("1. reward = {}".format(eb.step_reward))
                    for ot in observer_towers:
                        two_closest_bullets = e.find_two_closest_bullets(ot)
                        if random.random() < 0.05 and len(ot.bullets) <ot.max_bullets and stopwatch_timer_bullet >= stopwatcht_at_bullet:
                            ot.make_bullet(e)
                            stopwatch_timer_bullet = 0

            smart_enemies = new_smart_enemies 
           
            trainable_not_deleted_ut = True
            trainable_not_deleted_ot = True           
            for ut in user_towers:        
                (ut.bullets, trainable_not_deleted_ut, episode_reward, steps_count) = active_bullets_after_collision_checks (ut, smart_enemies, episode_reward, steps_count)
                trainable_enemy_exists = trainable_enemy_exists and trainable_not_deleted_ut
            for ot in observer_towers:        
                (ot.bullets, trainable_not_deleted_ot, episode_reward, steps_count) = active_bullets_after_collision_checks (ot, smart_enemies, episode_reward, steps_count)              
                trainable_enemy_exists = trainable_enemy_exists and trainable_not_deleted_ot
          
            for ed in smart_enemies:
                # print("2. end step trainable = {}".format(ed.trainable))
                if ed.trainable:
                    ed.rewards_history.append(ed.step_reward)
                    episode_reward += ed.step_reward
                    print("episode_reward= {}, steps_count = {}".format(episode_reward, steps_count))
                    
            
            #print("episode_reward= {}, steps_count = {}".format(episode_reward, steps_count))

            steps_count +=1
            if steps_count == max_steps_per_episode:                
                steps_count = 0
                for ed in smart_enemies:
                    if ed.trainable:
                        ed.learn(episode_reward)
                        ed.step_reward = 0
                
                episode_reward = 0
                print("Episode ENDED: episode_reward= {}, steps_count = {}".format(episode_reward, steps_count))
            
            

                
            
            ## PLOT
            screen.fill( myscreen.background_colour)
            myscreen.display_route(screen)    
            # my_second_enemy.display1(screen)
            for ut in user_towers:
                ut.display(screen)
                for b in ut.bullets:
                    b.display(screen)

            for ot in observer_towers:
                ot.display(screen)
                for b in ot.bullets:
                    b.display(screen)

            for eb in smart_enemies:
                e = eb.me_the_enemy
                e.display(screen)
            pygame.display.flip()



  

pygame.quit()

