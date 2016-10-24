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
    robot.set_head_angle(degrees(80.0)).wait_for_completed()
    waitForACubetap(robot)
    loop(robot)

def waitForACubetap(robot):
    print("looking for a cube ...")
    cubes = None
    robot.set_head_angle(degrees(0.0)).wait_for_completed()
    cubes = robot.world.wait_until_observe_num_objects(num=1, object_type=cozmo.objects.LightCube, timeout=60)
    cubes[0].set_lights(cozmo.lights.green_light)
    #look_around.stop()

    print("waiting for a tap")
    waiting_for_a_tap = True
    while waiting_for_a_tap:
        try:
            robot.world.wait_for(cozmo.objects.EvtObjectTapped)
            cubes[0].set_lights(cozmo.lights.red_light)
            waiting_for_a_tap = False
            continue
        except Exception as e:
            print("error waiting for a tap: %s" % e)
            pass
    print("TAP")

def useThisFace(face_to_follow):
    #print(face_to_follow)
    nice_pose = face_to_follow.pose
    #print(nice_pose)
    posey = nice_pose.position.y
    print(posey)
    if(posey < -15.0):
        #print("dude!")
        return posey
    return posey

def loop(robot):
    #look_around = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
    cozmoHeadAngle = 45.0
    face_to_follow = None
    do_the_loopy = True
    robot.set_head_angle(degrees(cozmoHeadAngle)).wait_for_completed()
    #robot.say_text("oh").wait_for_completed()

    while do_the_loopy:
        #print("looping ...")
        #face_to_follow = robot.world.wait_for_observed_face(timeout=30)
        #robot.say_text("Daniel... You are my friend!").wait_for_completed()
        turn_action = None
        if face_to_follow:
            # start turning towards the face
            if(face_to_follow.is_visible):
                theY = useThisFace(face_to_follow)
                #robot.set_head_angle(degrees(45.0)).wait_for_completed()

                if(theY < 50.0):
                    print("look up ...")
                    cozmoHeadAngle = cozmoHeadAngle + 5
                    robot.set_head_angle(degrees(cozmoHeadAngle)).wait_for_completed()
                else:
                    print("look down ...")
                    cozmoHeadAngle = cozmoHeadAngle - 5
                    robot.set_head_angle(degrees(cozmoHeadAngle)).wait_for_completed()
                robot.turn_towards_face(face_to_follow).wait_for_completed()
        if not (face_to_follow and face_to_follow.is_visible):
            # find a visible face, timeout if nothing found after a short while
            try:
                print("looking ...")
                face_to_follow = robot.world.wait_for_observed_face(timeout=10)
                if face_to_follow:
                    #print("face_to_follow=" + str(face_to_follow))
                    theY = useThisFace(face_to_follow)
                    robot.turn_towards_face(face_to_follow).wait_for_completed()
                    #robot.say_text("Dan!").wait_for_completed()
            except asyncio.TimeoutError:
                print("Didn't find a face!")
                robot.say_text("Where everybody go?", voice_pitch = 1.0, duration_scalar=0.7).wait_for_completed()
                robot.set_head_angle(degrees(45.0)).wait_for_completed()
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
        cozmo.run.connect_with_tkviewer(run)
        #cozmo.connect(run)
    except cozmo.ConnectionError as e:
        sys.exit("A connection error occurred: %s" % e)
