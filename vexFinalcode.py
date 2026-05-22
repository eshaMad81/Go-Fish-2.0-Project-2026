from vex import *

brain = Brain()

left_motor = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
right_motor = Motor(Ports.PORT10, GearSetting.RATIO_18_1, True)

MAX_SPEED = 15
TIMEOUT_MS = 500

last_msg_time = brain.timer.time(MSEC)

def clamp(val, low, high):
    if val < low:
        return low
    if val > high:
        return high
    return val

def move_robot(left_speed, right_speed):
    left_speed = clamp(left_speed, -MAX_SPEED, MAX_SPEED)
    right_speed = clamp(right_speed, -MAX_SPEED, MAX_SPEED)

    if left_speed > 1:
        left_motor.spin(FORWARD, left_speed, PERCENT)
    elif left_speed < -1:
        left_motor.spin(REVERSE, abs(left_speed), PERCENT)
    else:
        left_motor.stop()

    if right_speed > 1:
        right_motor.spin(FORWARD, right_speed, PERCENT)
    elif right_speed < -1:
        right_motor.spin(REVERSE, abs(right_speed), PERCENT)
    else:
        right_motor.stop()

def parse_command(cmd):
    try:
        parts = cmd.strip().split(",")

        if len(parts) != 2:
            return None

        left_speed = float(parts[0])
        right_speed = float(parts[1])

        return left_speed, right_speed

    except:
        return None

brain.screen.clear_screen()
brain.screen.print("Waiting for Pi")

buffer = ""

while True:
    # read all available characters from Pi
    while brain.serial.available() > 0:
        ch = brain.serial.read(1).decode()

        if ch == "\n":
            result = parse_command(buffer)
            buffer = ""

            if result is not None:
                left_speed, right_speed = result
                move_robot(left_speed, right_speed)
                last_msg_time = brain.timer.time(MSEC)

                brain.screen.clear_screen()
                brain.screen.set_cursor(1, 1)
                brain.screen.print("Pi connected")
                brain.screen.next_row()
                brain.screen.print("L:", left_speed)
                brain.screen.next_row()
                brain.screen.print("R:", right_speed)

        else:
            buffer += ch

            if len(buffer) > 30:
                buffer = ""

    # safety stop if Pi stops sending commands
    if brain.timer.time(MSEC) - last_msg_time > TIMEOUT_MS:
        move_robot(0, 0)

        brain.screen.set_cursor(5, 1)
        brain.screen.print("No recent command")

    wait(20, MSEC)
