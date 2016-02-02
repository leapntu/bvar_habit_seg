### PRELOADER
#uses a manifest file holding locations to and metadata concerning stimuli items, so they can be properly encasulated in Pyschopy objects
#stores all objects into a global dictionary called stimuli, using the id specified in the manifest file for access

from psychopy import visual, sound, event
import json, os

def make_stim(path, file_type, win): #function to convert file_type tags into Psychopy containers - handles file_types
  if file_type == 'movie':
    return visual.MovieStim(win, path)

  elif file_type == 'movie_loop':
    return visual.MovieStim(win, path, loop=True)

  elif file_type == 'audio':
    return sound.Sound(path)

  elif file_type == 'image':
    return visual.ImageStim(win, path)

def preload(manifest_path, win, stimuli): #logic for procssing manifest contents - handles path_types

  def pre():
    preload_text = "Please wait\n\nStimuli preloading"
    preload_message = visual.TextStim(win, text=preload_text, color='black')
    preload_message.draw()
    win.flip()

  def post():
    ready_text = "Ready to begin\n\nPress 's' to begin"
    ready_message = visual.TextStim(win, text=ready_text, color='black')
    ready_message.draw()
    win.flip()
    event.waitKeys(keyList=['s'])

  def load():
    manifest_file = open(manifest_path) #load manifest
    manifest_data = json.load(manifest_file) #parse manifest

    for item in manifest_data["stims"]:
      if item["path_type"] == "file":
        stimuli[item["id"]] = make_stim(item["path"], item["stimuli_type"], win)

      elif item["path_type"] == "dir_ord":
        #sort paths using ordering convention with filenames
        root = item["path"] # path to folder containing movie stims, NOTE use final '/' so can be concatinated with file names to make full paths
        filenames = [filename for filename in os.listdir(root) if not filename.startswith('.')] # get all file names in the movie folder set above (ignoring hidden files with list comprehension)
        filenames = [(int(f.split('.')[0]),f) for f in filenames]
        filenames = sorted(filenames, key=lambda n: n[0])
        filenames = [p for (n,p) in filenames]
        #go through filenames and add to a list at stimuli[id]
        stimuli[item["id"]] = []
        for filename in filenames:
          stimuli[item["id"]].append(make_stim(root+filename, item["stimuli_type"],win))

      elif item["path_type"] == "dir": #same as above dir behavior, but without ordering convention, so stimuli will appear in list in the same order used by OS to list directory contents
        root = item["path"]
        filenames = [filename for filename in os.listdir(root) if not filename.startswith('.')] # get all file names in the movie folder set above (ignoring hidden files with list comprehension)
        stimuli[item["id"]] = []
        for filename in filenames:
          stimuli[item["id"]].append(make_stim(root+filename, item["stimuli_type"],win))

  pre()
  load()
  post()
