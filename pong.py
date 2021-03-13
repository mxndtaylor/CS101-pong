# Source: http://www.codeskulptor.org/#user48_NSMe42Kl30l6x2p_6.py
# Implementation of classic arcade game Pong

import simplegui
import random
import math

#					#
#	  CONSTANTS		#
#					#

# generic constants
ZERO_VECTOR = (0, 0)
BOOLEAN_VECTOR = (0, 1)

# indexing constants for readability
LEFT, RIGHT = H_DIRECTIONS = BOOLEAN_VECTOR
UP, DOWN = V_DIRECTIONS = BOOLEAN_VECTOR
X, Y = COORDS = BOOLEAN_VECTOR

# board constants
BRD_W, BRD_H = BOARD_DIM = (600, 400)
HF_BRD_W, HF_BRD_H = (BRD_W / 2, BRD_H / 2)

# gutter contants
GUTTER_W = 8
GUTTERS = (GUTTER_W, BRD_W - GUTTER_W)

# score constants
SCORES_SIZE = 60
SCORES_POS_S = ([7 * BRD_W / 32, BRD_H / 5],
                [23 * BRD_W / 32, BRD_H / 5])
SCORES_START = ZERO_VECTOR

# ball contants
BALL_RADIUS = 20
BALL_START_VEL_RANGES = ((6, 12), (3, 9))
BALL_START_POS = (HF_BRD_W, HF_BRD_H)

# paddle constants
PAD_W, PAD_H = (GUTTER_W, 80)
HF_PAD_W, HF_PAD_H = (PAD_W / 2, PAD_H / 2)
PAD_X_POS_S = (HF_PAD_W, BRD_W - HF_PAD_W)
PAD_START_VEL_S = ZERO_VECTOR
PAD_START_POS_S = (HF_BRD_H, HF_BRD_H)
PAD_MOVE_SPEED = 15
PAD_MOVE_VEL_S = (-PAD_MOVE_SPEED, PAD_MOVE_SPEED)

#					#
#	  VARIABLES		#
#					#

# ball variables
BALL_POS = list(BALL_START_POS)
BALL_VEL = list(ZERO_VECTOR)

# paddle variables
PAD_POS_S = list(PAD_START_POS_S)
PAD_VEL_S = list(PAD_START_VEL_S)

# score variable
SCORES = list(SCORES_START)

#					#
#	HELPER FUNCS 	#
#					#
        
# calculates a interval from a center and a radius
def interval(center, radius):
    return [center - radius, center + radius]

# initialize pos and vel for new ball in middle of table
def spawn_ball(h_direction):
    global BALL_POS
    # spawns ball in middle
    BALL_POS = list(BALL_START_POS)
    
    # decides direction for horizontal velocity
    vel_signs = [1, -1]
    if h_direction is LEFT:
        vel_signs[X] = -1
    elif h_direction is RIGHT:
        vel_signs[X] = 1
        
    # builds BALL_VEL coordinate-wise
    vel_mags = [0,0]
    for coord in COORDS:
        vel_mags[coord] = random.randrange(*BALL_START_VEL_RANGES[coord])
        BALL_VEL[coord] = vel_signs[coord] * vel_mags[coord]

# calculates the corners of a paddle at the current position
def calc_paddle(side):
    pad_x, pad_y = PAD_X_POS_S[side], PAD_POS_S[side]
    left, right = interval(pad_x, HF_PAD_W)
    top, bottom = interval(pad_y, HF_PAD_H)
    corners = [[left, top], [right, top], 
               [right, bottom], [left, bottom]]
    return corners

# determines whether the ball has scored on a side
def ball_scored(side):
    pad_edges = interval(PAD_POS_S[side], HF_PAD_H)
    blocked = pad_edges[UP] <= BALL_POS[Y] <= pad_edges[DOWN]
    return not blocked

# updates ball position and velocity, 
#	returns the player who's scored, if any
def determine_ball():
    # calc allowed area for BALL_POS
    w_limits = interval(HF_BRD_W, HF_BRD_W - BALL_RADIUS)
    h_limits = interval(HF_BRD_H, HF_BRD_H - BALL_RADIUS)
    
    # determine if ball is in allowed area
    ball_in_x = w_limits[LEFT] < BALL_POS[X] < w_limits[RIGHT]
    ball_in_y = h_limits[UP] < BALL_POS[Y] < h_limits[DOWN]
    
    # if outside allowed vertical area then bounce it
    if not (ball_in_y):
        BALL_VEL[Y] *= -1
    
    # if outside allowed horizontal area
    #	then determine whether the ball has 
    # 	been blocked or scored and which side
    # 	scored, if any
    # 	if blocked, bounce ball and increase speed
    side_scored = None
    
    if not (ball_in_x):
        side_with_ball = int(HF_BRD_W < BALL_POS[X]) # true -> 1, false -> 0
        if ball_scored(side_with_ball):
            side_scored = abs(side_with_ball - 1)
        else:
            BALL_VEL[X] *= -1.1
            BALL_VEL[Y] *= 1.1

    # update ball position, return side scored if any
    BALL_POS[X] += BALL_VEL[X]
    BALL_POS[Y] += BALL_VEL[Y]
    return side_scored

# updates paddle position and velocity direction
def update_paddle(side):
    # shorten vel
    pad_vel = PAD_VEL_S[side]
    pad_pos = PAD_POS_S[side]
    
    # if pad is stopped, do nothing
    if pad_vel != 0:
        # calc allowed area for PAD_POS
        limits = HF_PAD_H, BRD_H - HF_PAD_H
        
        # determines if pad can move up or down
        pad_mobile = [limits[UP] < pad_pos, pad_pos < limits[DOWN]]
        
        # determines pad vel direction
        pad_vel_dir = PAD_MOVE_VEL_S.index(pad_vel)
        
        # if paddle can move in the direction it's going, let it
        if pad_mobile[pad_vel_dir]:
            PAD_POS_S[side] += pad_vel

# updates paddle velocity based on user input
def ctrl_pad_vel(side, v_direction):
    PAD_VEL_S[side] += PAD_MOVE_VEL_S[v_direction]

# draws a top to bottom vertical line
def draw_v_line(canvas, x_pos):
    canvas.draw_line([x_pos, 0], [x_pos, BRD_H], 1, "White")
    
#					#
#	EVENT HANDLERS 	#
#					#

def new_game():
    global PAD_POS_S, PAD_VEL_S, SCORES
    
    # reset paddles and scores
    SCORES = list(SCORES_START)
    PAD_POS_S = list(PAD_START_POS_S)
    PAD_VEL_S = list(PAD_START_VEL_S)
    
    # reset and randomize ball start
    h_direction = random.choice(H_DIRECTIONS)
    spawn_ball(h_direction)
    
def draw(canvas):
    # draw mid line
    draw_v_line(canvas, HF_BRD_W)
    
    # perform symmetric calculations
    for side in H_DIRECTIONS:
        # draw gutter, score, and paddle for each side
        draw_v_line(canvas, GUTTERS[side])
        canvas.draw_text(str(SCORES[side]), SCORES_POS_S[side],
                         SCORES_SIZE, "Gray")
        canvas.draw_polygon(calc_paddle(side), 
                                1, "White", "White")

        # update paddle position, keep on the screen
        update_paddle(side)
    
    # draw ball
    canvas.draw_circle(BALL_POS, BALL_RADIUS, 1, "White", "White")

    # determine ball state, keep on screen
    side_has_scored = determine_ball()

    # update play state
    if side_has_scored is not None:
        SCORES[side_has_scored] += 1
        spawn_ball(side_has_scored)

def keydown(key):
    if key == simplegui.KEY_MAP['w']:
        ctrl_pad_vel(LEFT, UP)
    elif key == simplegui.KEY_MAP['s']:
        ctrl_pad_vel(LEFT, DOWN)
    elif key == simplegui.KEY_MAP['up']:
        ctrl_pad_vel(RIGHT, UP)
    elif key == simplegui.KEY_MAP['down']:
        ctrl_pad_vel(RIGHT, DOWN)

def keyup(key):
    if key == simplegui.KEY_MAP['w']:
        ctrl_pad_vel(LEFT, DOWN)
    elif key == simplegui.KEY_MAP['s']:
        ctrl_pad_vel(LEFT, UP)
    elif key == simplegui.KEY_MAP['up']:
        ctrl_pad_vel(RIGHT, DOWN)
    elif key == simplegui.KEY_MAP['down']:
        ctrl_pad_vel(RIGHT, UP)

#					#
#	CREATE FRAME 	#
#					#

frame = simplegui.create_frame("Pong", BRD_W, BRD_H)
frame.add_button("New Game", new_game, 100)
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)


#					#
#	START FRAME 	#
#					#

new_game()
frame.start()
