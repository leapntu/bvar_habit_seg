from psychopy import visual, core, event, gui

import pyglet
import os
import random

from preloader import preload

# PSYCHOPY SETUP
# for variables used in all experiments, regardless of design, i.e. can
# likely copy into new experiment
# contains constants for key values, e.g. key.SPACE returns 32
key = pyglet.window.key
win = visual.Window([1366, 768])  # window setup
mode = ''  # dummy variable for state machine like behavior
clock = core.MonotonicClock()
stimuli = {}  # dictionary to populate with stimuli
info = []

def get_metadata():
  global info
  myDlg = gui.Dlg(title="JWP's experiment")
  myDlg.addText('Participant Information')
  myDlg.addField('Name:')
  myDlg.addField('Age:')
  myDlg.addText('Experiment Information')
  myDlg.addField('RA:')
  myDlg.show()
  if myDlg.OK:
      info = myDlg.data
  else:
      print 'user cancelled'

########### NON GENERIC SECTIONS ###########


# DATA VARIABLES & DATA OUTPUT FUNCTION
# for easy access to variables related to data collected
# defined before event handlers so data writing can happen on keypress

look_record = []
stimuli_record = []


def writeData():
  global info
  data_root = './data/'  # path to folder to write data
  raw_root = 'raw/'

  # determine which subject this is by taking the number of data files in
  # the directory (ignoring hidden files with list comprehension), adding
  # one, and converting to string
  subject = str(len([filename for filename in os.listdir(
      data_root + raw_root) if not filename.startswith('.')]) + 1)

  # generate output file name from collected info dialog and subject number
  raw_output = open(data_root + raw_root + subject + '_' + info[0] + '_' + info[1] + '_' + info[2] + '.csv', 'w')

  raw_output.write('look_record')
  for item in look_record:
    raw_output.write(',' + str(item))
  raw_output.write('\n')

  raw_output.write('stimuli_record')
  for item in stimuli_record:
    raw_output.write(',' + str(item[0]) + ';' + str(item[1]))
  raw_output.write('\n')

  raw_output.close()

  # os.system("files=./data/*_*;awk 'FNR==1 && NR!=1 { while (/^subj/)
  # getline; }1 {print}' $files > plp_data.csv") # get list of data files
  # and concatenate them to a single master file, using awk to remove
  # unwanted headers

# EXPERIMENT VARIABLES
# for variables specific to certain design, i.e. cannot likely be taken as
# is into new experiment
getter_done = 0  # boolean for attention getter status
counting = 0  # boolean for if look away counter is running

# KEY HANDLERS
# as per pyglet documentation, the following event logic is set for
# keydown and keyup events, respectively


def on_key_press(k, m):
  global look_record
  global getter_done
  global counting
  if k == key.SPACE:
    if mode in ['test', 'habit', 'getter']:
      look_record.append(clock.getTime())
      if mode in ['test', 'getter']:
        counting = 0
    if mode == 'getter':
      getter_done = 1


def on_key_release(k, m):
  global look_record
  global counting
  if k == key.SPACE:
    if mode in ['test', 'habit', 'getter']:
      look_record.append(clock.getTime())
      if mode in ['test', 'getter']:
        counting = 1

  if k == key.ESCAPE:
    writeData()
    win.close()
    core.quit()

# INFO
# pyglet window class instance is stored in the psyhopy.visual.Window object at winHandle
# the event handlers defined above must be added to it
# there are two event handler registration points: the low-level pyglet one inside the psychopy window, and the default psychopy.event
# the psychopy.event module is built on the underlying pyglet, so there
# seems to be no collisions

# add event handlers defined above to the low-level pyglet event listener
# at winHandle
win.winHandle.push_handlers(on_key_press, on_key_release)


# STIMULI HANDLERS & UTILITY FUNCTIONS
# for defining functions that control presentation of stimuli items

def sum_periods(start_index, stop_index):
  #calculate looking and away times between to indexes in the look_record
  looking = 0
  away = 0
  current_index = start_index
  if start_index == stop_index:
    return (0,0)
  while current_index != stop_index:
    if current_index % 2 == 0:
      looking += look_record[current_index + 1] - look_record[current_index]
      current_index += 1
      continue
    else:
      away += look_record[current_index + 1] - look_record[current_index]
      current_index += 1
      continue
  return (looking, away)

def sum_between(start_time, stop_time):
  #given two time points, calculate total looking and away times between them
  looking = 0
  away = 0
  start_index = 'none'
  stop_index = 'none'

  for index, time in enumerate(look_record):
    if start_index == 'none' and time > start_time:
      start_index = index
      break
    if start_index == 'none' and index == len(look_record) - 1:
      start_index = 'max'
  for index, time in enumerate(look_record[::-1]):
    if stop_index == 'none' and time < stop_time:
      stop_index = len(look_record) - 1 - index
      break

  print look_record
  print start_index, stop_index

  if type(start_index) == type(0) and type(stop_index) == type(0):
    looking, away = sum_periods(start_index, stop_index)
    if start_index % 2 == 0:
      away += look_record[start_index] - start_time
    else:
      looking += look_record[start_index] - start_time
    if stop_index % 2 == 0:
      looking += stop_time - look_record[stop_index]
    else:
      away += stop_time - look_record[stop_index]
    return (looking,away)

  elif start_index == 'max':
    distance = stop_time - start_time
    last_index = len(look_record) - 1
    if last_index % 2 == 0:
      looking += distance
    else:
      away += distance
    return (looking, away)

def habituate(playlist):
  global mode
  mode = 'habit'
  params = {}
  params['habituated'] = 0
  params['window'] = 30
  params['baseline'] = 0
  params['start'] = 0

  def get_baseline():
    start = params['start']
    window = params['window']
    now = clock.getTime()
    if now - start < window:
      return
    elif now - start >= window:
      params['baseline'] = sum_between(start,now)[0]
      params['check'] = window_wait

  def window_wait():
    if ( clock.getTime() - params['start'] ) <= (2.0 * params['window']):
      return
    else:
      params['check'] = check_habituation

  def check_habituation():
    now = clock.getTime()
    period_start = now - params['window']
    result = sum_between(period_start, now)

    if result[0] < ( params['baseline'] / 2.0 ):
      params['habituated'] = 1

  params['check'] = get_baseline
  params['start'] = clock.getTime()
  i = 0
  end = len(playlist)
  while i < end:
    if params['habituated'] == 1:
      break
    stimulus = playlist[i]
    stimulus_filename = stimulus.filename.split('/')[-1]
    stimulus_start = clock.getTime()
    stimuli_record.append((stimulus_filename, stimulus_start))
    while stimulus.status != visual.FINISHED:  # play until the movie is done
      params['check']()
      stimulus.draw()
      win.flip()
    stimuli_record.append((stimulus_filename, clock.getTime()))
    i += 1


def test(playlist):
  global getter_done
  global mode
  global counting

  for stimulus in playlist:
    stimulus_filename = stimulus.fileName.split('/')[-1]
    stimulus_end = stimulus.getDuration()


    #random.shuffle(stimuli["gets"])
    getter = stimuli["gets"][0]
    mode = 'getter'

    stimuli["ag"].play()
    while getter_done != 1:
      getter.draw()
      win.flip()
    stimuli["ag"].stop()
    getter_done = 0

    stimuli["checker"].draw()
    win.flip()

    stimulus.play()
    print stimulus
    stimulus_start = clock.getTime()
    mode = 'test'
    stimuli_record.append((stimulus_filename, stimulus_start))
    while clock.getTime() - stimulus_start <= stimulus_end:
      stimuli["checker"].draw()
      win.flip()
      if counting == 1 and clock.getTime() - look_record[-1] < 2:
        continue
      elif counting == 1 and clock.getTime() - look_record[-1] >= 2:
        stimulus.stop()
        counting = 0
        stimuli_record.append((stimulus_filename, clock.getTime()))
        break
      elif counting == 0:
        continue
    if clock.getTime() - stimulus_start > stimulus_end:
      stimuli_record.append((stimulus_filename, clock.getTime()))

# RUN EVENTS

get_metadata()

# pass the manifest file, the window object, and the stimuli dictionary
preload("load_manifest.json", win, stimuli)
random.shuffle(stimuli['words'])
random.shuffle(stimuli['parts'])
habituate(stimuli['fams'])
test(stimuli['words'])

writeData()

print look_record
print stimuli_record

win.close()
core.quit()
