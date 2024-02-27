from __future__ import division
from psychopy import visual, core, event, data, logging, monitors
import random
import ppc
import pandas as pd
import logging

def setParallelData(trigger_code):
    print(f"Mock trigger sent: {trigger_code}")  # Keep for debugging
    logging.info(f"Trigger sent: {trigger_code}")

# Initialize logging
logging.basicConfig(filename="experiment_log.log", level=logging.INFO, 
                    format='%(asctime)s.%(msecs)03d %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.info('Experiment started')


# Initialize the Clock and Window
MON_WIDTH = 34.5
MON_DISTANCE = 60.0
MON_SIZE = [1920, 1080]
FRAME_RATE = 60

trial_clock = core.Clock()
monotonic_clock = core.MonotonicClock()

my_monitor = monitors.Monitor('testMonitor', width=MON_WIDTH, distance=MON_DISTANCE)
my_monitor.setSizePix(MON_SIZE)
win = visual.Window(monitor=my_monitor, units='height', fullscr=True, allowGUI=False, color='black')
logging.info('Window and monitors initialized')

# Show Instructions
def show_instruction(text):
    logging.info(f"Displaying instruction: {text}")
    instruction = visual.TextStim(win, text=text, pos=(0, 0), color='white', wrapWidth=2.2, height=0.025)
    instruction.draw()
    win.flip()
    event.waitKeys(keyList=["space"])
    logging.info("Instruction ended")

# Prepare Stimuli
Cue_1 = 'Pictures/Cue1_hammer.png'
Cue_2 = 'Pictures/Cue2_cat.png'
cue_identifiers = {'Pictures/Cue1_hammer.png': 'Cue 1', 'Pictures/Cue2_cat.png': 'Cue 2'}
cues = list(cue_identifiers.keys())
words = {
    'ANIMAL': ["Zebra", "Tiger", "Shark", "Whale", "Eagle", "Otter", "Squid", "Skunk", "Sloth", "Snail", "Moose", "Crane", "Finch", "Gecko", "Horse", "Hyena", "Lemur", "Llama", "Panda", "Quail"],
    'TOOL': ["Drill", "Screw", "Clamp", "Level", "Wrench", "Lathe", "Chisel", "Anvil", "Brace", "Gauge", "Joint", "Knife", "Laser", "Mallet", "Nailer", "Plier", "Ruler", "Nozzle", "Crank", "Hammer"]
}
logging.info('Stimuli prepared')

# Auxiliary Functions
fixation = visual.TextStim(win, '+', height=0.05)
switch_count = 0

def get_category(cue):
    probabilities = cue_prob[cue]
    category = random.choices(population=list(probabilities.keys()), weights=list(probabilities.values()), k=1)[0]
    return category

def switch_probabilities():
    global switch_count
    logging.info('Switching probabilities')
    for cue in cue_prob:
        cue_prob[cue]['ANIMAL'], cue_prob[cue]['TOOL'] = cue_prob[cue]['TOOL'], cue_prob[cue]['ANIMAL']
    switch_count += 1

def show_fixation(duration_secs=1.5):
    logging.info('Showing fixation')
    num_frames = int(duration_secs * FRAME_RATE)  
    for frameN in range(num_frames):
        fixation.draw()
        win.flip()
    logging.info('Fixation ended')

def show_cue(cue, duration_secs=0.5):
    logging.info(f"Showing cue: {cue}")
    cue_duration_frames = int(duration_secs * FRAME_RATE)
    cue_onset = core.monotonicClock.getTime()
    cue_image = visual.ImageStim(win, image=cue, size=(0.20, 0.30))
    trigger_set = False

    for frameN in range(cue_duration_frames):
        if frameN == 0:
            win.callOnFlip(setParallelData, trigger_code)
            trigger_set = True
        cue_image.draw()
        win.flip()
        if frameN == 1 and trigger_set:
            win.callOnFlip(setParallelData, 0)
            trigger_set = False
    cue_offset = core.monotonicClock.getTime()
    logging.info(f"Cue shown: {cue} with duration {duration_secs} seconds")
    return cue_onset, cue_offset
#====================================================================

# Prediction Prompt
logging.info('Setting up prediction prompt')
prediction_slider = visual.Slider(win=win, ticks=[0, 1],
                                  labels=['ANIMAL', 'TOOL'],
                                  size=(0.25, 0.03),
                                  pos=(0, -0.05),
                                  style='radio',
                                  granularity=1,
                                  labelHeight=0.025)

text_prediction = visual.TextStim(win, text="Make a prediction.", pos=(0.0, 0.05), height=0.025, color='white')
keys_prediction = {'d': 0, 'k': 1}

def prediction_prompt(trigger_code, duration=1.5):
    logging.info('Starting prediction prompt')
    duration_frames = int(duration * FRAME_RATE)
    
    prediction_slider.markerPos = None
    event.clearEvents(eventType='keyboard')

    response_made = False
    reaction_time_prediction = None
    prediction = None

    pred_onset = core.monotonicClock.getTime()
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
                prediction_slider.markerPos = prediction
                response_made = True
                logging.info(f'Prediction made: {prediction} with reaction time: {reaction_time_prediction}')

        logging.info(f'Frame {frameN}: Before win.flip()')
        win.flip()
        logging.info(f'Frame {frameN}: After win.flip()')
        
    # Move the trigger reset to after the loop to control when it happens more explicitly
    logging.info('Setting trigger reset on next flip after prediction prompt')
    win.callOnFlip(setParallelData, 0)
    # Force a screen refresh here if needed to ensure the reset occurs at a controlled time
    win.flip()  # This ensures the callOnFlip action occurs at this specific flip
    logging.info('Trigger reset after prediction prompt')

    
    pred_offset = core.monotonicClock.getTime()
    logging.info('Prediction prompt completed')
    return prediction, reaction_time_prediction, pred_onset, pred_offset

# Word Stimulus
logging.info('Setting up word stimulus')
def show_word(category, trigger_code, word_duration_secs=0.5):
    logging.info(f'Showing word stimulus for category: {category}')
    word_duration_frames = int(word_duration_secs * FRAME_RATE)
    
    word_onset = core.monotonicClock.getTime()
    
    word = random.choice(words[category])
    word_text = visual.TextStim(win, text=word, pos=(0, 0), color='white', height=0.025)
    
    trigger_set = False
    
    for frameN in range(word_duration_frames):
        if frameN == 0:
            win.callOnFlip(setParallelData, trigger_code)
            trigger_set = True
        elif frameN == 1 and trigger_set:
            win.callOnFlip(setParallelData, 0)
            trigger_set = False
            
        word_text.draw()
        win.flip()
    
    word_offset = core.monotonicClock.getTime()
    logging.info(f'Word stimulus "{word}" shown for category: {category}')
    return word_onset, word_offset

# Data Saving
logging.info('Setting up data writer')
writer = ppc.csv_writer(filename_prefix='Sam_test',
                        folder='exp_data',
                        column_order=['Trial', 'Cue', 'Category', 'Prob_cat', 'CueOnset', 'CueOffset', 'Prediction', 'ReactionTime', 'PredOnset', 'PredOffset', 'WordOnset', 'WordOffset'])


#====================================================================
############################ MAIN LOOP ############################
#====================================================================

# Main Experiment Loop
logging.info('Main experiment loop starting')
n_trials = 2  # Adjust based on the experiment design
switch_trials = [1]  # Adjust based on when you want to switch probabilities
switch_trials = [x + 1 for x in switch_trials]

# Initial cue probabilities
cue_prob = {
    Cue_1: {'ANIMAL': 0.2, 'TOOL': 0.8},
    Cue_2: {'ANIMAL': 0.8, 'TOOL': 0.2}
}

# Trigger Codes
TRIGGER_CODES = {
    'prediction_start': 2,
    'word': 3,
}

show_instruction("The experiment will now begin. \n\n Press SPACE to START")

for trial in range(n_trials):
    logging.info(f'Starting trial {trial + 1}')
    trial_clock.reset()

    if trial + 1 in switch_trials:
        logging.info(f'Switching probabilities for trial {trial + 1}')
        switch_probabilities()

    cue = random.choice([Cue_1, Cue_2])
    category = get_category(cue)
    logging.info(f'Trial {trial + 1}: Selected cue "{cue}", Category: "{category}"')
    
    # Fixation Cross
    logging.info(f'Trial {trial + 1}: Showing fixation cross')
    show_fixation(1.5)
    logging.info(f'Trial {trial + 1}: Fixation cross ended, moving to cue')
    
    # Stimulus: Cue
    logging.info(f'Trial {trial + 1}: Showing cue')
    cue_onset, cue_offset = show_cue(cue, duration_secs=1.5)
    logging.info(f'Trial {trial + 1}: Cue completed, moving to fixation cross')
    
    # Fixation Cross
    logging.info(f'Trial {trial + 1}: Showing fixation cross again')
    show_fixation(1.5)
    logging.info(f'Trial {trial + 1}: Fixation cross ended, moving to word prediction prompt')
    
    # RESPONSE: Prediction
    logging.info(f'Trial {trial + 1}: Starting prediction prompt')
    prediction, reaction_time_prediction, pred_onset, pred_offset = prediction_prompt(TRIGGER_CODES['prediction_start'], duration=1.5)
    logging.info(f'Trial {trial + 1}: Prediction prompt completed, moving to fixation cross')
    
    # Fixation Cross
    logging.info(f'Trial {trial + 1}: Showing fixation cross')
    show_fixation(1.5)
    logging.info(f'Trial {trial + 1}: Fixation cross ended, moving to word stimulus')
    
    # Stimulus: Word
    logging.info(f'Trial {trial + 1}: Showing word stimulus')
    word_onset, word_offset = show_word(category, TRIGGER_CODES['word'], word_duration_secs=1.5)
    logging.info(f'Trial {trial + 1}: Word stimulus ended')

    # Define congruency based on switch count
    prob_cat = "Congruent" if switch_count % 2 == 0 else "Incongruent"
    logging.info(f'Trial {trial + 1}: Congruency category - {prob_cat}')

    # Log trial data
    trial_data = {
        'Trial': trial + 1,
        'Cue': cue_identifiers[cue],
        'Category': category,
        'Prob_cat': prob_cat,
        'CueOnset': cue_onset, 
        'CueOffset': cue_offset,
        'Prediction': prediction,
        'ReactionTime': reaction_time_prediction,
        'PredOnset': pred_onset,
        'PredOffset': pred_offset,
        'WordOnset': word_onset,
        'WordOffset': word_offset
    }
    logging.info(f'Trial {trial + 1}: Data logged')
    writer.write(trial_data)

logging.info('Main experiment loop ended')
