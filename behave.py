#!/usr/bin/env python3

'''

 === BEHAVE ===
Oh do behave!

'''
import sys
import cozmo
from cozmo.util import degrees
import asyncio
import time

def run(sdk_conn):
    '''init'''
    robot = sdk_conn.wait_for_robot()
    robot.move_lift(-3)
    robot.set_head_angle(degrees(20.0)).wait_for_completed()
    loop(robot)

def loop(robot):
    face_to_follow = None
    '''The main loop'''
    do_the_loopy = True
    robot.say_text("oh").wait_for_completed()

    while do_the_loopy:
        #print("looping ...")
        #face_to_follow = robot.world.wait_for_observed_face(timeout=30)
        #robot.say_text("Daniel... You are my friend!").wait_for_completed()
        turn_action = None
        if face_to_follow:
            # start turning towards the face
            if(face_to_follow.is_visible):
                print(face_to_follow)
            #turn_action = robot.turn_towards_face(face_to_follow)
            #robot.say_text("peekaboo").wait_for_completed()

        if not (face_to_follow and face_to_follow.is_visible):
            # find a visible face, timeout if nothing found after a short while
            try:
                print("looking ...")
                face_to_follow = robot.world.wait_for_observed_face(timeout=3)
                if face_to_follow:
                    #print("face_to_follow=" + str(face_to_follow))
                    robot.say_text("Daniel... You are my friend!").wait_for_completed()
            except asyncio.TimeoutError:
                print("Didn't find a face!")
                robot.say_text("Where everybody go?", voice_pitch = 1.0, duration_scalar=0.7).wait_for_completed()
                #do_the_loopy = False
                #return
            except KeyboardInterrupt:
                print("")
                print("Exit requested by user")
                do_the_loopy = False
                return

            if turn_action:
                # Complete the turn action if one was in progress
                print("starting turn_action.wait_for_completed()")
                turn_action.wait_for_completed()
                print("finished turn_action.wait_for_completed()")

        if do_the_loopy:
            #print("sleeping ...")
            time.sleep(.1)
        else:
            print("done now, goodbye")
            #pass


if __name__ == '__main__':
    cozmo.setup_basic_logging()

    try:
        cozmo.connect(run)
    except cozmo.ConnectionError as e:
        sys.exit("A connection error occurred: %s" % e)
