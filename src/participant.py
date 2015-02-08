from json import load

from os import listdir, makedirs
from os.path import exists, join

from Tkinter import (
                     Tk,
                     Button, Entry, Label, Listbox, Radiobutton, Checkbutton,
                     IntVar, StringVar,
                     DISABLED, END, W
)

from settings import DATA_DIR, EXP_NAME, TOTAL_SESSIONS


class Participant(object):
    """
    Creates the input frame and stores the information regarding the
    participant
    """
    def __init__(self, parent, *args, **kwargs):
        """
        Initialize the input frame and call to inititialize the user
        interface
        """
        # Set the Tk as the parent
        self.parent = parent
        # Initialize the user interface
        self.initUI()

    def initUI(self):
        """
        Initializes the user interface

        Setting up the entry widgets for:
        - Experiment_ID
        - Participant Name
        - Session Day
        - Pupil Size
        - Practice
        - Stereo
        """
        # Set the title
        self.parent.title(EXP_NAME)

        # Create the label for Experiment_ID and set location
        label_id = Label(text='Participant ID:')
        label_id.place(x=20, y=20)

        # Check the DATA_DIR directory for previous participants
        # and choose the next Experiment_ID in line
        self.folders = listdir(DATA_DIR)
        # Initiate Tkinter's StringVar
        self.value_id = StringVar()
        # Set the default value
        self.value_id.set('001')
        # Going in reverse order of the participants' directories in
        # DATA_DIR, find the last participant's Experiment_ID and opt
        # for the next one in line
        for folder in reversed(self.folders):
            try:
                # Check if the value of the first 3 digits of the
                # directory name is greater than the default value
                if int(folder[:3]) >= int(self.value_id.get()):
                    # Get the next Experiment_ID in integer form and
                    # convert to string format
                    num = str(int(folder[:3]) + 1)
                    # Actions to perform in case scenarios for each
                    # of the possibilites of num_length
                    num_length = {
                                  3: num,
                                  2: '0%s' % num,
                                  1: '00%s' % num
                    }
                    # Set the value accordingly to the StringVar,
                    # replacing the default
                    self.value_id.set(num_length[len(num)])
            # In case there are other folders in DATA_DIR, for which
            # the first 3 characters are not digits, we must cater
            # for when an exception is thrown up
            except ValueError:
                pass
        # Create the entry widget for Experiment_ID with the preset
        # value and state disabled
        self.input_id = Entry(self.parent, width=5, state=DISABLED,
                              textvariable=self.value_id)
        self.input_id.place(x=150, y=20)

        # Create the label for Participant Name and set location
        label_name = Label(text='Participant Name:')
        label_name.place(x=20, y=50)

        # Initiate Tkinter's StringVar
        self.value_name = StringVar()
        # Set the default value
        self.value_name.set('')
        # Create the entry for Participant Name and set location
        self.input_name = Entry(self.parent, width=35,
                                textvariable=self.value_name)
        self.input_name.place(x=150, y=50)
        self.input_name.focus()

        # Create the label for Session Day and set location
        label_day = Label(text='Session Day:')
        label_day.place(x=20, y=80)

        # Create value holder for Session Day as IntVar and set default
        # value to 1
        self.value_day = IntVar()
        self.value_day.set(1)
        # Create the radiobuttons as required
        for day in range(1, TOTAL_SESSIONS + 1):
            input_day = Radiobutton(self.parent, text=str(day),
                                    variable=self.value_day, value=day)
            # Anchor them to the West (W)
            input_day.pack(anchor=W)
            # Choose location for the radiobuttons
            input_day.place(x=150, y=(50 + (day * 25)))

        # Create the label for Pupil Size and set location
        label_pupilsize = Label(text='Pupil Size:')
        label_pupilsize.place(x=20, y=140)

        self.value_pupilsize = StringVar()
        self.value_pupilsize.set('')
        # Create the MaxLengthEntry for Pupil Size and set location
        # The maximum length is set to 3 characters and a float must be
        # provided
        self.input_pupilsize = MaxLengthEntry(self.parent, width=5,
                                              maxlength=3,
                                              required_type=float)
        self.input_pupilsize.config(textvariable=self.value_pupilsize)
        self.input_pupilsize.place(x=150, y=140)

        # Create value folder for Practice as IntVar
        self.value_practice = IntVar()
        # Create the checkbutton for Practice and set location
        input_practice = Checkbutton(self.parent, text='Practice',
                                     variable=self.value_practice, onvalue=1,
                                     offvalue=0)
        input_practice.place(x=150, y=170)

        # Create value holder for Stereo as IntVar
        self.value_stereo = IntVar()
        # Create the checkbutton for Stereo and set location
        input_stereo = Checkbutton(self.parent, text='Stereo',
                                   variable=self.value_stereo, onvalue=1,
                                   offvalue=0)
        input_stereo.place(x=150, y=200)

        # Create the label for Previous Subjects and set location
        label_previous = Label(text='Previous Subjects:')
        label_previous.place(x=20, y=250)

        # Create the Listboc containing all the previous participants
        self.input_previous = Listbox(self.parent, width=35, height=10)
        for identifier in self.folders:
            self.input_previous.insert(END, identifier)
        self.input_previous.place(x=150, y=250)
        self.input_previous.bind('<<ListboxSelect>>', self.__select_previous)

        # Create the submit button, give command upon pressing and set
        # location
        submit = Button(text='Submit', width=47, command=self.gather_input)
        submit.pack(padx=8, pady=8)
        submit.place(x=20, y=425)

    def __select_previous(self, event):
        """
        Handle scenario where user selects one of the previous participants
        """
        # Collect from previous subjects, if it was chosen
        self.previous = self.input_previous.curselection()
        if self.previous:
            self.previous = self.folders[int(self.previous[0])]
            with open(join(DATA_DIR, self.previous, 'data.json')) as f:
                data = load(f)
                # Set the value for participant ID
                self.value_id.set(data['ID'])
                # Set the value for name and disable the user from making
                # any more changes
                self.value_name.set(data['Name'])
                self.input_name.config(state=DISABLED)
                # Set the value for pupilsize and disable the user from
                # making any more changes
                self.value_pupilsize.set(data['Pupil Size'])
                self.input_pupilsize.config(state=DISABLED)

    def gather_input(self):
        """
        Gather the input from the Tkinter window and store it as class
        variables of the Participant class

        This module will also create a folder for the participant if
        it does not exist already in DATA_DIR
        NOTE: DATA_DIR is set in settings.py
        """
        # Collect all the values input and convert to their appropriate
        # types
        self.subject_id = self.input_id.get()
        self.name = self.input_name.get().title()
        self.day = int(self.value_day.get())
        try:
            self.pupilsize = float(self.input_pupilsize.get())
        except ValueError:
            pass
        self.practice = bool(self.value_practice.get())
        self.stereo = bool(self.value_stereo.get())

        # Destroy the Tkinter window
        self.parent.destroy()

        # Put together the directory name and path
        self.subject_dir = '%s_%s' % (self.subject_id,
                                      self.name.replace(' ', ''))
        self.subject_dir = join(DATA_DIR, self.subject_dir)
        # If the directory for the participant does not exist, create it
        if not exists(self.subject_dir):
            makedirs(self.subject_dir)


class ValidatingEntry(Entry):
    """
    A base class for validating entry widgets in Tkinter
    """
    def __init__(self, master, value="", **kw):
        apply(Entry.__init__, (self, master), kw)
        self.__value = value
        self.__variable = StringVar()
        self.__variable.set(value)
        self.__variable.trace("w", self.__callback)
        self.config(textvariable=self.__variable)

    def __callback(self, *dummy):
        value = self.__variable.get()
        newvalue = self.validate(value)
        if newvalue is None:
            self.__variable.set(self.__value)
        elif newvalue != value:
            self.__value = newvalue
            self.__variable.set(self.newvalue)
        else:
            self.__value = value

    def validate(self, value):
        """
        Override this to perform validation
        """
        return value


class MaxLengthEntry(ValidatingEntry):
    """
    Ensures that the variable passed to this Entry widget does not
    exceed a certain number of characters in length

    This custom class also ensures that the input is of integer type
    """
    def __init__(self, master, value="", maxlength=None,
                 required_type=None, **kw):
        self.maxlength = maxlength
        self.required_type = required_type
        apply(ValidatingEntry.__init__, (self, master), kw)

    def validate(self, value):
        if self.maxlength is None or len(value) <= self.maxlength:
            if not self.required_type:
                return value
            try:
                if value:
                    self.required_type(value)
                    return value
            except ValueError:
                return None
        # New value too long or is of the wrong type
        return None


def init_input():
    """
    Initialize the Participant class and collect input data and pass
    to the main Controller class
    """
    root = Tk()
    root.geometry('380x460')
    participant = Participant(root)
    root.mainloop()

    # If the Participant instance does not have all the information required
    # return None and let the Controller handle the issue
    if hasattr(participant, 'subject_id') and hasattr(participant, 'name')\
       and hasattr(participant, 'day') and hasattr(participant, 'pupilsize')\
       and hasattr(participant, 'practice') and hasattr(participant, 'stereo'):
        return participant
    else:
        return None


if __name__ == '__main__':
    """
    NOTE: For testing purposes only
          The experiment should be run using main.py
    """
    exp = init_input()
