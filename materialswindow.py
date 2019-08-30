from tkinter import Listbox, Menu, filedialog, Entry, Label, Button, Scrollbar, Frame
from tkinter import messagebox, NSEW, END, EW, NS, W, E, VERTICAL
from materials import TMaterial

class TMaterialsWindow(Frame):
    """
    Class represents auxiliary window containg materials database.
    """
    def __init__(self, master, TApp, TShapesWindow):
        """
        Call the parent class constructor and initialise object variables.
        """
        super().__init__()
        self.TApp = TApp
        self.TShapesWindow = TShapesWindow
        self.round_digits = 2
        self.init_widgets ()
        # Bind this class methods to manin menubar
        self.TApp.file_menu.entryconfig("Open materials", command = self.open_file)
        self.TApp.file_menu.entryconfig("Save materials", command = self.save_file)
        
    def init_widgets(self):
        """
        Initialise widgets.
        """
        # Set weights for columns and rows
        for i in range(6):
            self.grid_columnconfigure (i, weight = 1, uniform = "material_cols", minsize = 50)
        self.grid_rowconfigure (1, weight = 1)
        # self.grid_rowconfigure (2, weight = 1)

        # Create and arrange widgets (using grid)
        self.open_file_button = Button(self, text = "Open", command = self.open_file)
        self.open_file_button.grid(row = 0, column = 0, sticky = NSEW, columnspan = 3, padx = 20, pady = 5)
        self.save_file_button = Button(self, text = "Save", command = self.save_file)
        self.save_file_button.grid(row = 0, column = 3, sticky = NSEW, columnspan = 3, padx = 20, pady = 5)

        # ListBox
        self.materials_list = Listbox(self, exportselection = False)
        self.materials_list.grid(row = 1, column = 0, columnspan = 6, sticky = NSEW, padx = (5, 25), pady = 5)
        self.materials_list.bind("<<ListboxSelect>>", self.material_list_selected_item)

        # ListBox's y-scrollbar
        self.materials_list_scrollbar = Scrollbar(self, orient = VERTICAL, command = self.materials_list.yview)
        self.materials_list_scrollbar.grid(row = 1, column = 5, sticky = NS + E, padx = (0, 5), pady = 5)
        self.materials_list.config(yscrollcommand = self.materials_list_scrollbar.set)

        self.name_label = Label(self, text = "Name", anchor = W)
        self.name_label.grid(row = 2, column = 0, columnspan = 1, sticky = EW)
        self.name_entry = Entry(self, text = "")
        self.name_entry.grid(row = 2, column = 1, columnspan = 5, sticky = NSEW, padx = 5, pady = 2)
        self.epsilon_r_label = Label(self, text = "\u03b5r", anchor = W)
        self.epsilon_r_label.grid(row = 3, column = 0, columnspan = 1, sticky = EW)
        self.epsilon_r_entry = Entry(self, text = "")
        self.epsilon_r_entry.grid(row = 3, column = 1, columnspan = 5, sticky = NSEW, padx = 5, pady = 2)
        self.sigma_label = Label(self, text = "\u03c3", anchor = W)
        self.sigma_label.grid(row = 4, column = 0, columnspan = 1, sticky = EW)
        self.sigma_entry = Entry(self, text = "")
        self.sigma_entry.grid(row = 4, column = 1, columnspan = 5, sticky = NSEW, padx = 5, pady = 2)
        self.mu_r_label = Label(self, text = "\u03bcr", anchor = W)
        self.mu_r_label.grid(row = 5, column = 0, columnspan = 1, sticky = EW)
        self.mu_r_entry = Entry(self, text = "")
        self.mu_r_entry.grid(row = 5, column = 1, columnspan = 5, sticky = NSEW, padx = 5, pady = 2)
        self.sigma_mag_label = Label(self, text = "\u03c3*", anchor = W)
        self.sigma_mag_label.grid(row = 6, column = 0, columnspan = 1, sticky = EW)
        self.sigma_mag_entry = Entry(self, text = "")
        self.sigma_mag_entry.grid(row = 6, column = 1, columnspan = 5, sticky = NSEW, padx = 5, pady = 2)

        self.store_changed_params_button = Button(self, text = "Change", command = self.store_material_parameters)
        self.store_changed_params_button.grid(row = 7, column = 0, columnspan = 2, sticky = NSEW, padx = 5, pady = 5)
        self.delete_material_button = Button(self, text = "Delete", command = self.delete_material)
        self.delete_material_button.grid(row = 7, column = 2, columnspan = 2, sticky = NSEW, padx = 5, pady = 5)
        self.add_material_button = Button(self, text = "Add", command = self.add_material)
        self.add_material_button.grid(row = 7, column = 4, columnspan = 2, sticky = NSEW, padx = 5, pady = 5)

    def open_file(self):
        """
        Read an ASCII file containing materials data.
        """
        filename = filedialog.askopenfilename(initialdir = '.', title = "Select file", \
                    filetypes = [("All files", "*.*")])
        
        try:
            # Check, if given name is empty string
            if(filename == ""):
                raise Exception("No filename given!")
            # Check, if given file is binary
            if(self.is_binary(filename)):
                raise Exception("Designated file is binary!")
            else:
                file = open(filename, "rt")
        except Exception as message:
            messagebox.showerror("File error", message)
            return

        try:
            self.TApp.material = []
        except Exception as message:
            messagebox.showerror("Materials list error", message)
            return

        # Loop reading and parsing all lines one by one
        line_num = 1
        try:
            for line in file:
                if(line[0] != "#"):
                    # Omit lines that don't begin with hash sign (comments)
                    continue
                else:
                        tokens = line.split()
                        if(len(tokens) == 6):
                            epsilon_r = float(tokens[1])
                            sigma = float(tokens[2])
                            mu_r = float(tokens[3])
                            sigma_mag = float(tokens[4])
                            name = str(tokens[5])
                            self.TApp.materials.append(TMaterial(epsilon_r = epsilon_r, \
                                                                 sigma = sigma, \
                                                                 mu_r = mu_r, \
                                                                 sigma_mag = sigma_mag,\
                                                                 name = name))
                        else:
                            raise Exception("Invalid number of inputs in line {}!".format(line_num))
                line_num += 1
        except Exception as message:
            messagebox.showerror("Invalid input format", message)
            self.TApp.materials = []
            self.materials_list.delete(0, self.materials_list.size () )
            return
        finally:
            file.close()

        # Check wether any materials were read
        if(len(self.TApp.materials) == 0):
            messagebox.showwarning("Empty file", "File does not contain any materials' information.")

        # Repleace material's list
        self.update_list(self.TApp.materials)
    
    def save_file(self):
        """
        Save current materials database to an ASCII file.
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
            return
        
        try:
            if(len(self.TApp.materials) == 0):
                raise Exception ("Materials' list is empty!")
            else:
                for single_material in self.TApp.materials:
                    file.write("# " + str(single_material.epsilon_r) + " " + \
                               str(single_material.sigma) + \
                               " " + str (single_material.mu_r) + " " + \
                               str(single_material.sigma_mag) + " " + \
                               str(single_material.name) + "\n")
                file.close()
        except Exception as message:
            messagebox.showerror("Error while writing file", message)
            return
        finally:
            file.close()
        
    
    def update_list(self, materials):
        """
        Update shapes list.

        :param materials: new materials database.
        :type materials: list
        """
        self.materials_list.delete(0, self.materials_list.size())
        i = 0
        info_string = ""
        materials_names_str = ["pec", "free_space"]
        for single_material in materials:
            info_string += str(single_material.name) + ": " + str(single_material.epsilon_r)+ " " + str(single_material.sigma) + " " + \
                str(single_material.mu_r) + " " + str(single_material.sigma_mag)
            materials_names_str.append(str(single_material.name))
            try:
                self.materials_list.insert (i, info_string)
            except Exception as message:
                messagebox.showerror ("List error", message)
                self.materials_list.delete (0, self.materials_list.size () )
                return None
            i += 1
            info_string = ""
        # Update shapes window combobox
        self.TShapesWindow.material_box.config(values = materials_names_str)

    def get_selected_item_num(self):
        """
        Retrieve a index of a selected material on the list.

        :rtype: integer
        """
        try:
            selection = self.materials_list.curselection()
            return selection[0]
        # except Exception as message:
        except:
            #messagebox.showerror("No material selected!", message)
            return -1

    def material_list_selected_item(self, event):
        """
        Display selected material parameters in the text fields.

        :param event: listbox LMB click event.
        :type event: tkinter.Event
        """
        item_num = self.get_selected_item_num()
        if(item_num < 0):
            return None
        else:
            try:
                material = self.TApp.materials[item_num]
            except Exception as message:
                messagebox.showerror("Materials' list error", message)
                return None

        self.name_entry.delete(0, END)
        self.name_entry.insert(0, material.name)
        self.epsilon_r_entry.delete(0, END)
        self.epsilon_r_entry.insert(0, material.epsilon_r)
        self.sigma_entry.delete(0, END)
        self.sigma_entry.insert(0, material.sigma)
        self.mu_r_entry.delete(0, END)
        self.mu_r_entry.insert(0, material.mu_r)
        self.sigma_mag_entry.delete(0, END)
        self.sigma_mag_entry.insert(0, material.sigma_mag)

        self.materials_list.activate(item_num)
    
    def store_material_parameters(self):
        """
        Update material parameters from values entered in the text fields.
        """
        item_num = self.get_selected_item_num()
        if(item_num < 0):
            return None
        else:
            try:
                self.TApp.materials[item_num].name = str(self.name_entry.get())
                self.TApp.materials[item_num].epsilon_r = float(self.epsilon_r_entry.get())
                self.TApp.materials[item_num].sigma = float(self.sigma_entry.get())
                self.TApp.materials[item_num].mu_r = float(self.mu_r_entry.get())
                self.TApp.materials[item_num].sigma_mag = float(self.sigma_mag_entry.get())
                self.update_list(self.TApp.materials)
                self.materials_list.select_set(item_num)
            except Exception as message:
                messagebox.showerror("Materials' list error", message)

    def delete_material(self):
        """
        Delete a material from the database.
        """
        item_num = self.get_selected_item_num()
        if (item_num < 0):
            return None
        else:
            try:
                del self.TApp.materials[item_num]
                self.update_list(self.TApp.materials)
                if(item_num == 0):
                    self.materials_list.select_set(0)
                else:
                    self.materials_list.select_set(item_num - 1)
            except Exception as message:
                messagebox.showerror("Materials' list error", message)

    def add_material(self):
        """
        Add a material to the database.
        """
        try:
            if(str(self.name_entry.get()) == ""):
                raise Exception("Material can't have name that's an empty string!")
            self.TApp.materials.append(TMaterial(epsilon_r = float(self.epsilon_r_entry.get()), \
                                                 sigma = float(self.sigma_entry.get()),\
                                                 mu_r = float(self.mu_r_entry.get()), \
                                                 sigma_mag = float(self.sigma_mag_entry.get()), \
                                                 name = str(self.name_entry.get())))
        except Exception as message:
            messagebox.showerror("Error while creating material", message)
        self.update_list(self.TApp.materials)
        self.materials_list.select_set(END)

    def is_binary(self, filename):
        """
        Check wether given file is binary (that is non-text).
        """
        try:
            with open(filename, 'tr') as check_file:    # try open file in text mode
                check_file.read()
                return False
        except:                                         # if it fails then file is non-text (binary)
            return True
        finally:
            check_file.close()
