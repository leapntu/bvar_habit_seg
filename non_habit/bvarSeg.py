from psychopy import visual, core, event, gui, sound
import pyglet, os, random

###Variable Declaration###

mode = '' # dummy variable to track program state condition
counting = 0 # set to zero when not counting how long the child has been looking away, and set to one if counting how long child has been looking away
look_away_time = 0 # when child looks away during test phase, get the time, and use it to keep checking if two seconds have passed

stim_start_stim = 0

get_done = 0 # flags the getter as being done or not

data = [] # to hold collected data points
key = pyglet.window.key # contains constants for key values, e.g. key.SPACE returns 32
win = visual.Window([800,600]) # create psychopy window object
clock = core.MonotonicClock() # create sub-ms accurate clock that starts counting up from zero upon creation

info = [] # to hold initial metadata results
stimuli = '' # to hold current stimuli filename
look_onset = 0.0
click_stim = '' # to hold stimuli that was playing during click
space_down = 0.0 # create global place holder for clock time that space is pressed
space_time = 0.0 # create global place holder for time space was pressed (space_down minus clock time when space is released)

famStart = 0 # holds the start time of the familiarization / habituation phase

#Collect File Paths

fam_root = './stimuli/famil/' # path to folder containing movie stims, NOTE use final '/' so can be concatinated with file names to make full paths
fam_paths = [ filename for filename in os.listdir(fam_root) if not filename.startswith('.')] # get all file names in the movie folder set above (ignoring hidden files with list comprehension)
fam_paths = [ (int(f.split('.')[0]),f) for f in fam_paths]
fam_paths = sorted(fam_paths, key=lambda n: n[0])
fam_paths = [ p for (n,p) in fam_paths]
fam_playlist = [] # create a placeholder for the movie stims created below to be itterated through

part_root = './stimuli/part/'
part_paths = [ filename for filename in os.listdir(part_root) if not filename.startswith('.')] # get all file names in the movie folder set above (ignoring hidden files with list comprehension)
part_paths = [ (int(f.split('.')[0]),f) for f in part_paths]
part_paths = sorted(part_paths, key=lambda n: n[0])
part_paths = [ p for (n,p) in part_paths]
part_playlist = [] # create a placeholder for the movie stims created below to be itterated through

word_root = './stimuli/words/'
word_paths = [ filename for filename in os.listdir(word_root) if not filename.startswith('.')] # get all file names in the movie folder set above (ignoring hidden files with list comprehension)
word_paths = [ (int(f.split('.')[0]),f) for f in word_paths]
word_paths = sorted(word_paths, key=lambda n: n[0])
word_paths = [ p for (n,p) in word_paths]
word_playlist = [] # create a placeholder for the movie stims created below to be itterated through

get_root = './stimuli/get/'
get_paths = [ filename for filename in os.listdir(get_root) if not filename.startswith('.')] # get all file names in the movie folder set above (ignoring hidden files with list comprehension)
get_playlist = [] # create a placeholder for the movie stims created below to be itterated through

data_root = './data/' # path to folder to write data
subject = str(len([ filename for filename in os.listdir(data_root) if not filename.startswith('.')]) + 1) # determine which subject this is by taking the number of data files in the directory (ignoring hidden files with list comprehension), adding one, and converting to string
# the writting of data files themselves is specified in the end of experiment section

###EVENT HANDLERS###

# as per pyglet documentation, the following event logic is set for keydown and keyup events, respectively

#Define data write function before event handler definition

def writeData():
    conditionCount[condition] += 1
    counterFile = open('conditionCounter.txt','w')
    counterFile.write('varset,'+str(conditionCount['varset'])+'\n')
    counterFile.write('scramble,'+str(conditionCount['scramble']))
    counterFile.close()

    if info == [] or info[0] == '': #if metadata box was canceled or no subject name recoreded, set to 'unknown'
        info.append('unknown')

    output = open(data_root+subject+'_'+info[0]+'.csv','w') # generate output file name from collected info dialog and subject number

    header = 'subject, stim, rt, type\n'

    output.write(header)

    for (stim, rt, rt_type) in data:
        output.write(subject+','+stim+','+rt+','+rt_type+'\n')

    output.close()

    #os.system("files=./data/*_*;awk 'FNR==1 && NR!=1 { while (/^subj/) getline; }1 {print}' $files > plp_data.csv") # get list of data files and concatenate them to a single master file, using awk to remove unwanted headers

    print data


def on_key_press(k,m):
    if k == key.SPACE:
        global space_down
        global stimuli
        global click_stim
        global look_onset
        global mode
        global counting
        global get_done
        if mode == "test" and counting == 1:
            counting = 0
            space_time = (clock.getTime() - look_away_time ) * 1000
            data.append( ( click_stim, str(space_time), "under2" ) )

        elif mode == 'get':
            get_done = 1
            mode = "test"
            look_onset = clock.getTime()
            click_stim = stimuli
            space_down = clock.getTime()

        else:
            look_onset = clock.getTime()
            click_stim = stimuli
            space_down = clock.getTime()


def on_key_release(k,m):
    if k == key.SPACE:
        global space_down
        global space_time
        global data
        global click_stim
        global look_onset
        global mode
        global counting
        global look_away_time
        if mode == "test" and counting == 0:
            counting = 1
            look_away_time = clock.getTime()
        elif mode == "get":
            pass
        else:
            space_time = (clock.getTime() - space_down) * 1000 #return time in milliseconds
            data.append(  ( click_stim, str(space_time), "between_spaces" )  ) #data to be written to the output file is added to the data array above on each key release, and some globals are updated, i.e. 'stimuli' are updated as the experiment executes

    if k == key.ESCAPE:
        writeData()
        win.close()
        core.quit()

#pyglet window class instance is stored in the psyhopy.visual.Window object at winHandle
#the event handlers defined above must be added to it
#there are two event handler registration points: the low-level pyglet one inside the psychopy window, and the default psychopy.event
#the psychopy.event module is built on the underlying pyglet, so there seems to be no collisions

win.winHandle.push_handlers(on_key_press, on_key_release) #add event handlers defined above to the low-level pyglet event listener at winHandle

###LOAD & PACKAGE STIMULI###

#Images
start_background = test_background = visual.ImageStim(win, './stimuli/check.jpg')
#test_background = visual.ImageStim(win, './stimuli/checkerboard.jpg')
start_text = visual.TextStim(win, text='Press S To Start', color='red')

#Movies
for path in fam_paths:
       fam_playlist.append(visual.MovieStim(win, fam_root+path))

for path in part_paths:
    part_playlist.append(sound.Sound(part_root+path))


for path in word_paths:
    word_playlist.append(sound.Sound(word_root+path))


for path in get_paths:
    get_playlist.append(visual.MovieStim(win, get_root+path, loop=True))

###EXPERIMENT###

#Meta Data
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

#Start Screen
start_background.draw()
start_text.draw()
win.flip()
event.waitKeys(keyList=['s'])

#Play Movies

# for movie in fam_playlist[:1]:
#     stimuli = movie.filename.split('/')[-1] # split filename property of stimuli, which is the file path, then take the last element, the filename
#     while movie.status != visual.FINISHED: # play until the movie is done
#         movie.draw()
#         win.flip()

#word_playlist = [word_playlist[1],word_playlist[2],word_playlist[4],word_playlist[3]]
#part_playlist = [part_playlist[0],part_playlist[16],part_playlist[13],part_playlist[12]]

random.shuffle(word_playlist)
random.shuffle(part_playlist)

mode = 'test'
for i in range(4):
    for list in [word_playlist, part_playlist]:
        random.shuffle(get_playlist)
        stimuli = list[i].fileName.split('/')[-1]
        stim = list[i]
        get = get_playlist[0]
        get_done = 0
        mode = 'get'
        while get_done != 1:
            get.draw()
            win.flip()
        #Start processing a test stimuli
        end = stim.getDuration()
        start = clock.getTime()
        test_background.draw()
        win.flip()
        stim.play()
        while clock.getTime() - start < end: # play until the sound is done
            win.flip()
            if clock.getTime() - start < 8:
                if counting == 1 and clock.getTime() - look_away_time < 2:
                    continue
                elif counting == 1 and clock.getTime() - look_away_time >= 2:
                    stim.stop()
                    counting = 0
                    space_time = (look_away_time - space_down ) * 1000
                    data.append( ( click_stim, str(space_time), "over2" ) )
                    break
                else:
                    continue
            elif clock.getTime() - start >= 8:
                stim.stop()
                stim.status = 'done'
                break
        if stim.status == 'done' and counting == 0:
            space_time = (clock.getTime() - space_down ) * 1000
            data.append( ( click_stim, str(space_time), "full_look" ) )
        elif stim.status == 'done' and counting == 1:
            counting = 0
            space_time = (look_away_time - space_down ) * 1000
            data.append( ( click_stim, str(space_time), "end_while_away" ) )


#mode = 'final'
#
#while get_done != 1:
#    get.draw()
#    win.flip()
#    for button in event.getKeys():
#        if button in ['n']:
#            get_done = 1

#End Of Experiment

if info == [] or info[0] == '': #if metadata box was canceled or no subject name recoreded, set to 'unknown'
    info.append('unknown')

output = open(data_root+subject+'_'+info[0]+'.csv','w') # generate output file name from collected info dialog and subject number

header = 'subject, stim, rt_type\n'

output.write(header)

for (stim, rt, rt_type) in data:
    output.write(subject+','+stim+','+rt+','+rt_type+'\n')

output.close()

#os.system("files=./data/*_*;awk 'FNR==1 && NR!=1 { while (/^subj/) getline; }1 {print}' $files > plp_data.csv") # get list of data files and concatenate them to a single master file, using awk to remove unwanted headers

print data

win.close()
core.quit()
