from tkinter import simpledialog, scrolledtext, INSERT, Button, Frame, LEFT, messagebox, filedialog, END

class TOutputPreviewWindow(simpledialog.Dialog):
    """
    Class represents output file contents preview window.

    :param master: master window object.
    :type master: tkinter.Tk
    :param out_string: contents of the gprMAx input file.
    :type out_string: string
    """
    def __init__(self, master, output_string):
        """
        Initialise object variables and call the parent class constructor.
        """
        self.output_string = output_string
        super().__init__(master)

    def body(self, master):
        """
        Initialise widgets.

        :param master: master window object.
        :type master: tkinter.Tk
        """
        self.output_preview = scrolledtext.ScrolledText(self)
        self.output_preview.pack()
        self.output_preview.insert(INSERT, self.output_string)
        return self.output_preview
    
    def apply(self):
        """
        Return requested inputs.
        """
        filename = filedialog.asksaveasfilename(initialdir = '.', title = "Select file", \
                                                filetypes = [("All files", "*.*")])
        try:
            # Check, if given name is empty string
            if(filename == ""):
                raise Exception("No filename given!")
            else:
                file = open(filename, "wt")
        except Exception as message:
            messagebox.showerror("File error", message)
            return None
        
        try:
            file.write(self.output_preview.get("1.0", END))
        except Exception as message:
            messagebox.showerror("Error while writing file", message)
        finally:
            file.close()
        self.result = filename
        self.destroy()

    def cancel(self):
        """
        Destroy window upon clicking Cancel button.
        """
        self.destroy()

    def buttonbox(self):
        """
        Redefine default Ok/Cancel buttons in the bottom of the window with
        Save/Cancel.
        """
        self.bbox = Frame(self)
        self.save_button = Button(self.bbox, text = "Save", width = 10, command = self.apply)
        self.save_button.pack(side = LEFT, padx = 5, pady = 5)
        self.cancel_button = Button(self.bbox, text = "Cancel", width = 10, command = self.cancel)
        self.cancel_button.pack(side = LEFT, padx = 5, pady = 5)
        self.bbox.pack()