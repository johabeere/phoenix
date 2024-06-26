import Hardware as hw
import Helper as h

def main():
    #hw.hw_init()
    input("press when you are ready for mounting")
    hw.set_mounting()
    input("press when I should move into storage position")
    hw.set_servo_percent(h.parameters['Hardware']['drop_servo'], h.parameters['Hardware']['flying_position'])
    hw.hw_cleanup()
    exit(0)



if __name__ == "__main__": 
    main()