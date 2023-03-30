from tkinter import *
import subprocess

# TKinter setup
root = Tk()
root.overrideredirect(True)
root.geometry('242x378+200+200')
root.title("FlameSearch")
root.configure(bg='#2a2b2c')

# Moves the window when dragging the top bar
# Teleports the window to a certain position
# but otherwise works fine
def move_window(event):
    root.geometry('+{0}+{1}'.format(event.x_root-55, event.y_root-10))

# Update the color of the close button when hovered over
def close_hover(event):
    global close_button
    close_button['bg']='#cd4142'

# Update the color of the close button when clicked
def close_normal(event):
    global close_button
    close_button['bg']='#994142'

# Custom minimal top bar to match the theme of the rest of the gui
# The default bar is hidden  
title_bar = Frame(root, relief='raised', bd=0, bg='#404142', height=5)
close_button = Button(title_bar, command=root.destroy, bd=0, width=3, bg='#994142', activebackground='red')
title_bar.place(x = 0, y = 0, height = 20, relwidth = 1.0)
close_button.pack(side=RIGHT)
title_bar.bind('<B1-Motion>', move_window)
close_button.bind('<Enter>', close_hover)
close_button.bind('<Leave>', close_normal)

# Custom widget for building the main part of the gui
# Builds on the default tkinter frame widget
# Very closely resembles the in game GUI
class LevelSlider(Frame):
    def __init__(self, parent, name='', num=0):
        Frame.__init__(self, parent)
        # Load the images screenshotted and cleaned up from RimWorld
        self.oneflameimage = PhotoImage(file = "clearone.png")
        self.twoflameimage = PhotoImage(file = "cleartwo.png")
        # Set the color of the background and remove borders
        self.canvas = Canvas(self, bg='#2a2b2c', bd=0, highlightthickness=0)
        
        # Create tkinter canvases with the images and hide them
        # Clicking in the canvas area updates which flame level (0-2) is shown 
        self.oneflame = self.canvas.create_image(103, 10, image = self.oneflameimage, state='hidden')
        self.twoflame = self.canvas.create_image(103, 10, image = self.twoflameimage, state='hidden')

        # Rectangle that has a changing width to act as a slider and match the appearance of the game
        # which I couldn't get with the default slider
        self.rect = self.canvas.create_rectangle(116, 0, 117, 24, fill='#404142', width=0)

        # Helvetica is the font used in the game, but Unity supports custom kerning
        # while tkinter's font rendering does not, so while it's close, it doesn't quite
        # perfectly match the game's appearance
        self.text = self.canvas.create_text(5 + 116, 13, text="0", fill='#e6e6e6', font=('Helvetica', 10), anchor='w')
        self.name = self.canvas.create_text(6, 11, text=name, fill='#e6e6e6', font=('Helvetica', 10), anchor='w')
        
        # When left click is dragged, update the "slider"
        # Only works within the slider area
        self.canvas.bind('<B1-Motion>', self.update_width)

        # When the flame area is clicked, cycle through the levels
        self.canvas.bind('<ButtonPress-1>', self.update_flames)

        # Changes the background to highlight the active element
        self.canvas.bind('<Enter>', self.on_enter)
        self.canvas.bind('<Leave>', self.on_leave)

        # Absolute positioning to match the game's appearance
        self.canvas.place(x=0, y=0, width=230, height=24)
        
        # Keep track of which slider is which
        self.number = num
        # Holds the value of the slider for later use
        self.level = 0
        # Holds the level of the flame for later use
        self.flame = 0
    
    # Updates the width of the rectangle and the number displayed
    def update_width(self, e):
        # These numbers make it snap to match the game pixel perfect
        # They also constrain updating the slider to only the slider area of the widget
        pos = round((e.x-117)/5.69)
        # Can only be a value between 0 and 20
        if pos <= 20 and pos >= 0:
            self.canvas.coords(self.rect, 116, 0, 116 + round(pos*5.69) + 1, 24)
            self.canvas.itemconfigure(self.text, text=str(pos))
            self.level = pos

    # Cycles through the flame level
    def update_flames(self, e):
        # Updates the flame level only if clicked within the area
        # to the left of the slider area
        # Also updates which image is shown
        if e.x <= 117:
            self.flame += 1
            if self.flame == 1:
                self.canvas.itemconfigure(self.oneflame, state='normal')
            elif self.flame == 2: 
                self.canvas.itemconfigure(self.twoflame, state='normal')
                self.canvas.itemconfigure(self.oneflame, state='hidden')
            else:
                self.canvas.itemconfigure(self.twoflame, state='hidden')
                self.canvas.itemconfigure(self.oneflame, state='hidden')
                self.flame = 0
        else:
            # If it's not outside the slider area, allows for updating the
            # slider with a click instead of needing to drag
            self.update_width(e)
    
    # Update the background color to highlight when active
    def on_enter(self, e):
        self.canvas.config(bg='#404142')
        self.canvas.itemconfigure(self.rect, fill='#535455')
    def on_leave(self, e):
        self.canvas.config(bg='#2a2b2c')
        self.canvas.itemconfigure(self.rect, fill='#404142')

# List of all the skill options to label the custom widget        
options = ["Shooting", "Melee", "Construction", "Mining", "Cooking", "Plants", "Animals", "Crafting", "Artistic", "Medical", "Social", "Intellectual"]

# Generate all the elements with a for loop and the list instead of hardcoding
# Makes it easy to add more if more are added to either the base game
# or through a mod
sliders = []
for number, option in enumerate(options):
    sliders.append(LevelSlider(root, option, number))
    sliders[number].place(x = 6, y = ( number * 27 ) + 28, width = 230, height = 24)

# Gets the needed values from all the sliders to pass to the separate search.py
def search():
    # Collect the values to convert and concatenate into a single string
    args = ' '.join(','.join([str(i.number+1), str(i.flame), str(i.level)]) for i in sliders if i.flame > 0 or i.level > 0)
    # Run search.py in the background with all the values in as arguments
    subprocess.Popen("python search.py " + args, shell=True)

# Add a button to the bottom
button = Button(root, text = "Search", command = search, width = 50, bg='#404142', fg='#e6e6e6', bd=0)
button.pack(side = BOTTOM)

# Make sure the window is always on top, 
# otherwise it gets lost when the search starts
root.call('wm', 'attributes', '.', '-topmost', '1')
root.mainloop()
