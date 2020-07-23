try:
    from Tkinter import *
    import tkSimpleDialog
except:
    from tkinter import *
    import tkinter.simpledialog as tkSimpleDialog


class ParamsDialog(tkSimpleDialog.Dialog):
    """A dialog to get the hardware parameters"""
    
    def body(self, main):

        self.wm_iconbitmap('linearIcon.ico')
        self.title('Choose Hardware Parameters')

        self.result = False
        
        self.deviceLabel = Label(main, text='Device')
        self.deviceLabel.grid(row=0, column=0, columnspan=2, sticky=SW)
        self.deviceCombo = Combobox(main, ['DC718', 'DC890'], relief=RIDGE, bd=4, textWidth=20)
        self.deviceCombo.grid(row=1, column=0, columnspan=2, sticky=NW)

        self.nChannelsLabel = Label(main, text='# Channels')
        self.nChannelsLabel.grid(row=2, column=0, columnspan=2, sticky=SW)
        self.nChannelsText  = StringVar()
        self.nChannelsText.set('1')
        self.nChannelsEntry = Entry(main, textvariable=self.nChannelsText)
        self.nChannelsEntry.grid(row=3, column=0, columnspan=2, sticky=NW)

        self.nBitsLabel = Label(main, text='# Bits')
        self.nBitsLabel.grid(row=4, column=0, sticky=SW)
        self.nBitsText  = StringVar()
        self.nBitsText.set('16')
        self.nBitsEntry = Entry(main, textvariable=self.nBitsText)
        self.nBitsEntry.grid(row=5, column=0, sticky=NW, padx=5)

        self.alignmentLabel = Label(main, text='Alignment')
        self.alignmentLabel.grid(row=4, column=1, sticky=SW)
        self.alignmentText  = StringVar()
        self.alignmentText.set('16')
        self.alignmentEntry = Entry(main, textvariable=self.alignmentText)
        self.alignmentEntry.grid(row=5, column=1, sticky=NW, padx=5)

        self.isBipolar = IntVar()
        self.isBipolarCheck = Checkbutton(main, text='Bipolar', variable=self.isBipolar)
        self.isBipolarCheck.grid(row=0, column=2, rowspan=2, sticky=W)

        self.clockEdgeLabel = Label(main, text='Clock Edge')
        self.clockEdgeLabel.grid(row=2, column=2, sticky=SW)
        self.clockEdgeCombo = Combobox(main, ['POS_EDGE', 'NEG_EDGE'], relief=RIDGE, bd=4, textWidth=20)
        self.clockEdgeCombo.grid(row=3, column=2, sticky=NW)

        self.fpgaLoadLabel = Label(main, text='FPGA Load')
        self.fpgaLoadLabel.grid(row=4, column=2, sticky=SW)
        self.fpgaLoadCombo = Combobox(main, ['NONE', 'CMOS', 'LVDS', 'S1407', 'S1408', \
                                               'S2308', 'S2366', 'DCMOS', 'DLVDS'], \
                                      relief=RIDGE, bd=4, textWidth=20)
        self.fpgaLoadCombo.grid(row=5, column=2, sticky=NW)
        
        return None
        
    def apply(self):
        self.result = True

    def values(self):
        return (self.deviceCombo.value(), int(self.nChannelsText.get()), int(self.nBitsText.get()), \
                int(self.alignmentText.get()), bool(self.isBipolar.get()), \
                1-self.clockEdgeCombo.value(), self.fpgaLoadCombo.value())

class Combobox(Frame):
    '''A compound widget that lets you type or pick from a drop-down'''
    def __init__(self, main, entries, textWidth=None, **options):
    
        self.main = main
    
        Frame.__init__(self, main, options)
        
        # keep track of the items
        self.entries = entries
        
        ## the drop-down menu button
        
        # down-arrow image for button
        IMAGE_DATA = """
        #define im_width 16
        #define im_height 16
        static char im_bits[] = {
        0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xf9,0x9f,0xf1,0x8f,0xe3,0xc7,
        0xc7,0xe3,0x8f,0xf1,0x1f,0xf8,0x3f,0xfc,0x7f,0xfe,0xff,0xff,0xff,0xff,0xff,0xff
        };
        """
        self.downImage = BitmapImage(data=IMAGE_DATA, foreground="white", background="black")
        
        # the button
        self.menuButton = Button(self, image=self.downImage, command=self.showMenu)
        self.menuButton.grid(row=0, column=0)
        
        ## the text box
        self.text = StringVar()
        if textWidth == None:
            self.textEntry = Entry(self, textvariable=self.text)
        else:
            self.textEntry = Entry(self, textvariable=self.text, width=textWidth)
        self.textEntry.grid(row=0, column=1) 
               
    def showMenu(self):
        
        # the menu
        menu = Menu(self, tearoff=0)
                     
        for entry in self.entries:
            menu.add_radiobutton(label=entry, variable=self.text, 
                value=entry, indicatoron=False)
        
        x = self.textEntry.winfo_rootx()
        y = self.textEntry.winfo_rooty() + self.textEntry.winfo_height()
        menu.post(x, y)
        
    def setState(self, state):
    
        self.menuButton.configure(state=state)
        self.textEntry.configure(state=state)

    def value(self):
        return self.entries.index(self.text.get())

# run a quick test if run standalone        
if __name__ == "__main__":

    root = Tk()
    root.withdraw()

    dlg = ParamsDialog(root)
    root.destroy()
    if dlg.result:
        print(dlg.deviceCombo.text.get(), dlg.nChannelsText.get(), dlg.nBitsText.get(), \
              dlg.alignmentText.get(), dlg.isBipolar.get(), dlg.clockEdgeCombo.text.get(), \
              dlg.fpgaLoadCombo.text.get())
        print(dlg.values())
    
