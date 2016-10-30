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

class Contextable(object):
    head_degrees = 0
    robot = None
    # The class "constructor" - It's actually an initializer
    def __init__(self, head_degrees):
        self.head_degrees = head_degrees

    def setRobot(self, robot):
        self.robot = robot


def make_contextable(head_degrees):
    ctx = Contextable(head_degrees)
    return ctx

def run(sdk_conn):
    '''init'''
    robot = sdk_conn.wait_for_robot()
    ctx = make_contextable(80.0)
    ctx.setRobot(robot)
    ctx.robot.move_lift(-3)
    ctx.robot.set_head_angle(degrees(ctx.head_degrees)).wait_for_completed()
    waitForACubetap(ctx)
    loop(ctx)

def tryForThreeCubes(ctx):
    cubes = []
    timout_in = 5
    #look_around = None
    ctx.robot.set_head_angle(degrees(ctx.head_degrees)).wait_for_completed()
    print("looking for some cubes ...")
    print("three")
    cubes = ctx.robot.world.wait_until_observe_num_objects(num=3, object_type=cozmo.objects.LightCube, timeout=timout_in)
    #print(cubes)
    if(cubes == []):
        print("two")
        cubes = ctx.robot.world.wait_until_observe_num_objects(num=2, object_type=cozmo.objects.LightCube, timeout=timout_in)
        if(cubes == []):
            print("one")
            cubes = ctx.robot.world.wait_until_observe_num_objects(num=1, object_type=cozmo.objects.LightCube, timeout=timout_in)
    return cubes

def waitForACubetap(ctx):
    cubes = []
    look_around = None
    ctx.head_degrees = 0.0
    while(cubes == []):
        cubes = tryForThreeCubes(ctx)
        if(cubes == []):
            print("looking around")
            look_around = ctx.robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
    if(look_around != None):
        look_around.stop()

    cube_length = len(cubes)
    print(str(cube_length) + " cubes found")
    for cube in cubes:
        cube.set_lights(cozmo.lights.green_light)

    #look_around.stop()

    print("waiting for a tap")
    waiting_for_a_tap = True
    while waiting_for_a_tap:
        try:
            ctx.robot.world.wait_for(cozmo.objects.EvtObjectTapped)
            cubes[0].set_lights(cozmo.lights.red_light)
            waiting_for_a_tap = False
            continue
        except Exception as e:
            print("still waiting for a tap: %s" % e)

    #which block was tapped?
    #the_chosen_block = cubes.tapped_one
    print("TAPPED")
    ctx.head_degrees = 45.0
    ctx.robot.set_head_angle(degrees(ctx.head_degrees)).wait_for_completed()

def useThisFace(face_to_follow):
    #print(face_to_follow)
    nice_pose = face_to_follow.pose
    #print(nice_pose)
    posey = nice_pose.position.y
    #print(posey)
    if(posey < -15.0):
        #print("dude!")
        return posey
    return posey

def faceYouIteration(ctx):
    do_the_loopy = True
    ctx.head_degrees = 45.0
    face_to_follow = None
    turn_action = None
    if face_to_follow:
        # start turning towards the face
        if(face_to_follow.is_visible):
            theY = useThisFace(face_to_follow)
            #robot.set_head_angle(degrees(45.0)).wait_for_completed()
            print("look down ...")
            if(theY < 120.0):
                print("theY ..." + theY)
                ctx.head_degrees = ctx.head_degrees + 5
                if(ctx.head_degrees > 45):
                    ctx.head_degrees = 45
                ctx.robot.set_head_angle(degrees(ctx.head_degrees)).wait_for_completed()
            else:
                print("look down ...")
                ctx.head_degrees = ctx.head_degrees - 5
                if(ctx.head_degrees < -25):
                    ctx.head_degrees = -25
                ctx.robot.set_head_angle(degrees(ctx.head_degrees)).wait_for_completed()
            ctx.robot.turn_towards_face(face_to_follow).wait_for_completed()
    if not (face_to_follow and face_to_follow.is_visible):
        # find a visible face, timeout if nothing found after a short while
        try:
            #("looking ...")
            face_to_follow = ctx.robot.world.wait_for_observed_face(timeout=10)
            if face_to_follow:
                #print("face_to_follow=" + str(face_to_follow))
                theY = useThisFace(face_to_follow)
                ctx.robot.turn_towards_face(face_to_follow).wait_for_completed()
                #robot.say_text("Dan!").wait_for_completed()
        except asyncio.TimeoutError:
            print("Didn't find a face!")
            ctx.robot.say_text("Where everybody go?", voice_pitch = 1.0, duration_scalar=0.7).wait_for_completed()
            ctx.robot.set_head_angle(degrees(45.0)).wait_for_completed()
            #do_the_loopy = False
            #return
        except KeyboardInterrupt:
            print("")
            print("Exit requested by user")
            do_the_loopy = False
            return False

        if turn_action:
            # Complete the turn action if one was in progress
            print("starting turn_action.wait_for_completed()")
            turn_action.wait_for_completed()
            print("finished turn_action.wait_for_completed()")
    return do_the_loopy

def loop(ctx):
    #look_around = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
    do_the_loopy = True
    ctx.robot.set_head_angle(degrees(ctx.head_degrees)).wait_for_completed()
    #robot.say_text("oh").wait_for_completed()

    while do_the_loopy:
        #print("looping ...")
        #face_to_follow = robot.world.wait_for_observed_face(timeout=30)
        #robot.say_text("Daniel... You are my friend!").wait_for_completed()
        do_the_loopy = faceYouIteration(ctx)

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
