from __future__ import division
from psychopy import visual, core, event, data, logging, monitors
import random
import ppc
import pandas as pd
#from triggers import setParallelData
def setParallelData(trigger_code):
    print(f"Mock trigger sent: {trigger_code}")
#==============================================
# Initialize the Clock and Window
#====================================================================

MON_WIDTH = 34.5  # monitor width in centimeters
MON_DISTANCE = 60.0  # viewer's distance from monitor in centimeters
MON_SIZE = [1920, 1080]  # monitor resolution in pixels
FRAME_RATE = 60

# Initialize the general clock
trial_clock = core.Clock()
# Initialize the monotonic clock
monotonic_clock = core.MonotonicClock()

# Create psychopy window
my_monitor = monitors.Monitor('testMonitor', width=MON_WIDTH, distance=MON_DISTANCE)
my_monitor.setSizePix(MON_SIZE)
win = visual.Window(monitor=my_monitor, units='height', fullscr=True, allowGUI=False, color='black')


#====================================================================
# Show Instructions
#====================================================================
def show_instruction(text):
    instruction = visual.TextStim(win, text=text, pos=(0, 0), color='white', wrapWidth=2.2, height=0.025)
    instruction.draw()
    win.flip()
    event.waitKeys(keyList=["space"])
"""
instruction_texts = [
    "Welcome to the word category prediction task! \n \n In this experiment, you'll guess the category of upcoming words.\n\n Press SPACE to see how it works..",
    "In each trial: \n\n 1. You'll see a cue. This gives you a hint about the category of the next word. \n\n 2. Based on the cue, you make your prediction. This is a binary outcome, you will predict either an ANIMAL or a TOOL. \n\n 3. You rate how confident you are with your decision on a scale from TOTAL GUESS to VERY CONFIDENT \n\n 4. You will be presented with a word, and you'll see if your prediction was correct \n\n Press SPACE to continue.",
    "Remember: \n\n Pay attention!  Cues and Words are going to be presented only for a very brief moment. \n\n Act fast!  You will only have a brief time to respond. \n\n Press SPACE to continue.",
    "Keys: \n\n Place your fingers on the keys: D-F-G | H-J-K \n\n  To make a prediction, press: \n\n\n\n ANIMAL                                                   TOOL\n  [ D ]                                                        [ K ] \n\n\n\n\n\n\n\n Press SPACE to continue.",
    "Confidence scale 0-5 \n\n 0 = Guess \n 5 = Confident \n\n  To rate your confidence, press: \n\n\n\n GUESS                                                                                     CONFIDENT \n\n 0                  1                  2                  3                  4                  5      \n [D]                [F]                [G]               [H]                [J]                [K]    \n\n\n\n\n\n\n\n Press SPACE to continue.",
]

for text in instruction_texts:
    show_instruction(text)
"""

#====================================================================
# Prepare Stimuli
#====================================================================

# Stimuli lists
Cue_1 = 'Pictures/Cue1_hammer.png'
Cue_2 = 'Pictures/Cue2_cat.png'

cues = [Cue_1, Cue_2]

#cues = {
#    'Cue 1': 'Pictures/Cue1_elefant.png',
#    'Cue 2': 'Pictures/Cue2_hammer.png'
#}
#cues = ['Pictures/Cue1_elefant.png', 'Pictures/Cue2_hammer.png']  
words = {'ANIMAL': ["Zebra", "Tiger", "Shark", "Whale", "Eagle", 
    "Otter", "Squid", "Skunk", "Sloth", "Snail",
    "Moose", "Crane", "Finch", "Gecko", "Horse",
    "Hyena", "Lemur", "Llama", "Panda", "Quail"], 
         
         'TOOL': ["Drill", "Screw", "Clamp", "Level", "Wrench",
    "Lathe", "Chisel", "Anvil", "Brace", "Gauge",
    "Joint", "Knife", "Laser", "Mallet", "Nailer",
    "Plier", "Ruler", "Nozzle", "Crank", "Hammer"]}

#====================================================================
# Auxilliary Functions
#====================================================================

# Fixation Cross
fixation = visual.TextStim(win, '+', height=0.05)

def get_category(cue):
    probabilities = cue_prob[cue]
    category = random.choices(population=list(probabilities.keys()), weights=list(probabilities.values()), k=1)[0]
    return category

switch_count = 0

def switch_probabilities():
    global switch_count
    for cue in cue_prob:
        cue_prob[cue]['ANIMAL'], cue_prob[cue]['TOOL'] = cue_prob[cue]['TOOL'], cue_prob[cue]['ANIMAL']
    switch_count += 1
#====================================================================



# Fixation cross
def show_fixation(duration_secs=1.5):
    num_frames = int(duration_secs * FRAME_RATE)  # Calculate the number of frames for the duration
    
    for frameN in range(num_frames):
        fixation.draw()
        win.flip()
#====================================================================

# Show Cue
def show_cue(cue, trigger_code, duration_secs=0.5):
    cue_duration_frames = int(duration_secs * FRAME_RATE)
    
    # Get current time as cue onset
    cue_onset = core.monotonicClock.getTime()
    
    # Prepare the cue 
    #cue_text = visual.TextStim(win, text=cue, pos=(0, 0), color='white', height=0.025)
    
    cue_image = visual.ImageStim(win, image=cue, size=(0.20, 0.30))
    
    # Variable to manage trigger state
    trigger_set = False

    for frameN in range(cue_duration_frames):
        if frameN == 0:
            # Set trigger only on the first frame
            win.callOnFlip(setParallelData, trigger_code)
            trigger_set = True
        cue_image.draw()
        win.flip()
        if frameN == 1 and trigger_set:
            # Reset trigger immediately after it's set, on the next frame
            win.callOnFlip(setParallelData, 0)
            trigger_set = False
    
    # Mark cue offset immediately after last flip
    cue_offset = core.monotonicClock.getTime()
    
    return cue_onset, cue_offset
#====================================================================



# Prediction Prompt
prediction_slider = visual.Slider(win=win, ticks=[0, 1],
                                  labels=['ANIMAL', 'TOOL'],
                                  size=(0.25, 0.03),
                                  pos=(0, -0.05),
                                  style='radio',
                                  granularity=1,
                                  labelHeight=0.025,
                                  )


text_prediction = visual.TextStim(win, text="Make a prediction.", pos=(0.0, 0.05), height=0.025, color='white')
keys_prediction = {'d': 0, 'k': 1}

def prediction_prompt(trigger_code, duration=1.5):
    duration_frames = int(duration * FRAME_RATE)
    
    prediction_slider.markerPos = None
    event.clearEvents(eventType='keyboard')

    response_made = False
    reaction_time_prediction = None
    prediction = None

    pred_onset = core.monotonicClock.getTime()

    # Turn the trigger on with the next screen refresh when the slider appears
    win.callOnFlip(setParallelData, trigger_code)

    for frameN in range(duration_frames):
        prediction_slider.draw()
        text_prediction.draw()

        if not response_made:
            keys = event.getKeys(keyList=['d', 'k'], timeStamped=core.monotonicClock)
            if keys:
                key, timeStamp = keys[0]
                prediction = keys_prediction[key]
                reaction_time_prediction = timeStamp

                # Once a response is made, update the slider position and prepare to turn off the trigger
                prediction_slider.markerPos = prediction
                response_made = True

        if frameN == duration_frames - 1:
            # Prepare to turn the trigger off after the last frame is drawn
            win.callOnFlip(setParallelData, 0)

        win.flip()
        
    pred_offset = core.monotonicClock.getTime()

    # Ensure the trigger is turned off if it hasn't been already
    setParallelData(0)

    return prediction, reaction_time_prediction, pred_onset, pred_offset
#====================================================================

 
 
# Word Stimulus
def show_word(category, trigger_code, word_duration_secs=0.5):

    word_duration_frames = int(word_duration_secs * FRAME_RATE)
    
    word_onset = core.monotonicClock.getTime()
    
    # Prepare the word 
    word = random.choice(words[category])
    word_text = visual.TextStim(win, text=word, pos=(0, 0), color='white', height = 0.025)
    
    # Set trigger to be sent on next flip, and reset after word is shown
    trigger_set = False
    
    for frameN in range(word_duration_frames):
        if frameN == 0:
            # Set trigger only on the first frame
            win.callOnFlip(setParallelData, trigger_code)
            trigger_set = True
        elif frameN == 1 and trigger_set:
            # Reset trigger immediately after it's set
            win.callOnFlip(setParallelData, 0)
            trigger_set = False
            
        word_text.draw()
        win.flip()
    
    # Mark word offset immediately after last flip
    word_offset = core.monotonicClock.getTime()
    
    return word_onset, word_offset
#====================================================================
# Data Saving
#====================================================================

# Example initialization
writer = ppc.csv_writer(filename_prefix='participant2',
                    folder='exp_data',
                    column_order=['Trial', 'Cue', 'Category', 'CueOnset', 'CueOffset', 'Prediction', 'ReactionTime', 'WordOnset', 'WordOffset'])


#====================================================================
############################ MAIN LOOP ############################
#====================================================================

n_trials = 10  # Adjust for the actual experiment
switch_trials = [4, 6, 8]  # Interval for switching probabilities
switch_trials = [x + 1 for x in switch_trials]

# Initial cue probabilities

cue_prob = {
    Cue_1: {'ANIMAL': 0.2, 'TOOL': 0.8},
    Cue_2: {'ANIMAL': 0.8, 'TOOL': 0.2}
}



# Trigger Codes
TRIGGER_CODES = {
    'cue': 1,  
    'prediction_start': 2,  
    'word': 3, 
}


show_instruction("The experiment will now begin. \n\n Press SPACE to START")

for trial in range(n_trials):
    trial_clock.reset()

    #if trial != 0 and trial % trial_switch_interval == 0:
    #    switch_probabilities()
    
    if trial + 1 in switch_trials:
        switch_probabilities()
    
    cue = random.choice([Cue_1, Cue_2])
    category = get_category(cue)
    
    # Fixation Cross 
    show_fixation(1.5)
    
    # Stimulus: Cue 
    cue_onset, cue_offset = show_cue(cue, TRIGGER_CODES['cue'], duration_secs=1.5)
    
    # Fixation Cross 
    show_fixation(1.5)
    
    # RESPONSE: Prediction 
    prediction, reaction_time_prediction, pred_onset, pred_offset = prediction_prompt(TRIGGER_CODES['prediction_start'], duration=1.5)
    
    # Fixation Cross 
    show_fixation(1.5)
    
    # Stimulus: Word 
    word_onset, word_offset = show_word(category, TRIGGER_CODES['word'], word_duration_secs=1.5)

    prob_cat = "Congruent" if switch_count % 2 == 0 else "Incongruent"

    # Log trial data
    trial_data = {
        'Trial': trial + 1, 
        'Cue': cue,
        'Category': category,
        'CueOnset': cue_onset,
        'CueOffset': cue_offset,
        'Prediction': prediction,
        'ReactionTime': reaction_time_prediction,
        'WordOnset': word_onset,
        'WordOffset': word_offset,
        'PredOnset': pred_onset,
        'PredOffset': pred_offset,
        'Prob_cat': prob_cat
    }
    writer.write(trial_data)


#====================================================================
# Logging the data
#====================================================================
