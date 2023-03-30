import numpy as np
import win32gui as wgui
import win32process as wproc
import win32api as wapi
import time, sys, mss
import pynput.mouse as mouse
from pynput import keyboard

# Get the arguments and remove the first one (search.py)
args = sys.argv
args.pop(0)

# Exit if there's nothing to do
if len(args) < 1:
    print("No arguments given")
    sys.exit()

# Get the number of things to match
to_match = len([i for i in ','.join(args).split(',') if i != '0']) - len(args)

# Start keeping track of how long it takes
# Depending on the arguments, it could take a while
init_time = time.time()

# Initialize the pynput mouse controller
m = mouse.Controller()

# Find the RimWorld window handle and don't continue if it's not found
# Should not run if the game is not open
hwnd = wgui.FindWindow(None, "RimWorld by Ludeon Studios")
if not hwnd:
    print("Is RimWorld running? Window not found.")
    sys.exit()
print(wgui.GetClientRect(hwnd))

# Set the RimWorld window to be focused so the chances of something
# unintentionally being autoclicked are lower
print("Window `{0:s}` handle: 0x{1:016X}".format("RimWorld by Ludeon Studios", hwnd))
remote_thread, _ = wproc.GetWindowThreadProcessId(hwnd)
wproc.AttachThreadInput(wapi.GetCurrentThreadId(), remote_thread, True)
prev_handle = wgui.SetFocus(hwnd)

# Get the corner coordinates of the window
rect = wgui.GetWindowRect(hwnd)
print(rect)

# Set the mouse position to be over the randomize button in advance
# The menu doesn't change with different resolutions, only the border
# around it, so the position relative to the center of the screen should stay the same
m.position = ((rect[0] + rect[2]) / 2 + 365, (rect[1] + rect[3]) / 2 - 280)

# Keybaord listening for emergency escape
# Execution can be stopped at any time by pressing the 'end' key
# May be better to change it to any keyboard keypress
def on_press(key):
    if key == keyboard.Key.end:
        # Stop listener
        return False
    try:
        print("alphanumeric key {0} pressed".format(key.char))
    except AttributeError:
        print("special key {0} pressed".format(key))

def on_release(key):
    print("{0} released".format(key))

# Start the keyboard listener and run in the background
# unaffected by later code execution
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

# Set the area of the screen to crop screenshots
# Same as the mouse position before, the coordinates
# should be correct for any resolution since it's relative
# to the center of the menu/screen 
fl_area = {
    "top": int(((rect[1] + rect[3]) / 2 - 173 - 107)),
    "left": int(((rect[0] + rect[2]) / 2 + 22)),
    "width": 345,
    "height": 297 + 108,
}
#print(fl_area)
print("Init time: {:.5} seconds".format(time.time() - init_time))

fl_time = time.time()
# Keep track of the number of times the mouse has been automatically clicked
click_count = 0

# Take a screenshot
with mss.mss() as sct:
    # Keep running the loop as long as there's no emergency escape
    while listener.running:
        # Keep track of how long it takes to check
        one_loop = time.time()

        # Will store the number of arguments that were matched to know when to stop
        matches = []

        # Set the mouse position again in case it was moved
        m.position = ((rect[0] + rect[2]) / 2 + 365, (rect[1] + rect[3]) / 2 - 280)
        

        for info in args:
            # Get one set of arguments
            s = [int(i) for i in info.split(',')]

            # Get a screenshot of the game menu area
            img = np.array(sct.grab(fl_area))
            
            # Check the red channel of certain pixels to check for the level of the skill
            # or the level of the flame, and if the level meets or exceeds the argument level
            # add it to 'matches'
            if s[1] == 1 and (img[((s[0] - 1) * 27) + 107][0][2] == 247 or img[((s[0] - 1) * 27) + 107][0][2] == 255):
                matches.append(s[1])
            elif s[1] == 2 and img[((s[0] - 1) * 27) + 107][0][2] == 247:
                matches.append(s[1])
            elif s[2] > 0 and img[((s[0] - 1) * 27) + 107][round(s[2] * 5.69) + 13][2] != 42:
                matches.append(s[2])
            else: 
                break
            print(s)
        print("Matches:", matches)
        #print("Time to check for flames: {:.5} seconds".format(time.time() - one_loop))

        if img[0][303][2] == 98 or img[0][303][2] == 106:
            # If the mouse isn't over the randomize button, start over without clicking
            continue
        elif len(matches) < to_match:
            # If there aren't enough matches and the mouse is over the randomize button
            # click it and check again
            m.press(mouse.Button.left)
            time.sleep(0.01)
            m.release(mouse.Button.left)
            m.release(mouse.Button.left)
            click_count += 1
        elif len(matches) == to_match:
            # If everything matches up, finish execution
            print("Flames matched in ", click_count, " clicks!")
            break
        else:
            # If somehow none of the other conditions are met
            # something went very wrong and I'll have to check the logic again
            print("Something went wrong")
            break
    
