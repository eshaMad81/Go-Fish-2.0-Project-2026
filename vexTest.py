from vex import *

brain = Brain()

left_motor = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
right_motor = Motor(Ports.PORT10, GearSetting.RATIO_18_1, True)

while True:

    brain.screen.clear_screen()
    brain.screen.print("LEFT")

    left_motor.spin(REVERSE, 15, PERCENT)
    right_motor.spin(FORWARD, 15, PERCENT)

    wait(2, SECONDS)

    left_motor.stop()
    right_motor.stop()

    wait(1, SECONDS)

    brain.screen.clear_screen()
    brain.screen.print("RIGHT")

    left_motor.spin(FORWARD, 15, PERCENT)
    right_motor.spin(REVERSE, 15, PERCENT)

    wait(2, SECONDS)

    left_motor.stop()
    right_motor.stop()

    wait(1, SECONDS)
