import os
import guilib as ui
import numpy as np

widgets = {
    "textbox": None, 
    "point": []
}

def sum_list(biglist):
    sumlist = []
    for eachlist in biglist:
        if eachlist == biglist[0]:
            for i, y in enumerate(eachlist):
                sumlist.append(y)
        else:
            for i, y in enumerate(eachlist):
                sumlist[i] = sumlist[i] + y
    return sumlist
    
def read_data(folder_path):
    all_intensity = []
    faulty_list = []
    filelist = os.listdir(folder_path)
    for eachfile in filelist:
        energy_tempo = []
        intensity_tempo = []
        path = os.path.join(folder_path, eachfile)
        try:
            with open(path) as source:
                for row in source.readlines():
                    if row == "\n":
                        pass
                    else:
                        try:
                            energy, intensity = row.split(" ")
                            energy_tempo.append(float(energy))
                            intensity_tempo.append(float(intensity))
                        except ValueError:
                            faulty_list.append(eachfile)
        except (IOError, UnicodeDecodeError):
            faulty_list.append(eachfile)
        else:
            if len(intensity_tempo) == 500:
                if len(energy_tempo) == 500:
                    all_intensity.append(intensity_tempo)
                    widgets["energy"] = energy_tempo
                else:
                    pass
            else:
                pass
    widgets["intensity"] = sum_list(all_intensity)
    return faulty_list
    
def open_folder():
    widgets["folderpath"] = ui.open_folder_dialog("Choose folder", r'C:\Users\Admin\Downloads\spektri')
    faultylist = read_data(widgets["folderpath"])
    if faultylist == []:
        pass
    elif len(faultylist) == 1:
        message1 = "Cannot read 1 file."
        ui.open_msg_window("Error message", message1, error=True)
    else:
        message2 = "Cannot read {} files.".format(len(faultylist))
        ui.open_msg_window("Error message", message2, error=True)
        
def choose_point(event):
    x = event.xdata
    y = event.ydata
    xlist = widgets["energy"]
    ylist = widgets["intensity"]
    for i, each_x in enumerate(xlist):
        if each_x <= x <= xlist[i+1]:
            if ylist[i] <= y <= ylist[i+1]:
                widgets["point"].append((x, y))
                message1 = "You have chosen x = {}, y = {}".format(x, y)
                ui.write_to_textbox(widgets["textbox"], message1)
            elif ylist[i] >= y >= ylist[i+1]:
                widgets["point"].append((x, y))
                message2 = "You have chosen x = {}, y = {}".format(x, y)
                ui.write_to_textbox(widgets["textbox"], message2)
            else:
                pass
        else:
            pass
            
def calculate_parameters(x1, y1, x2, y2):
    try:
        m = float((y2 - y1) / (x2 - x1))
        b = float((x2 * y1 - x1 * y2) / (x2 - x1))
    except ZeroDivisionError:
        message = "The line is vertical, it doesn't have an equation."
        ui.write_to_textbox(widgets["textbox"], message)
    else:
        return m, b
        
def only_peak():
    new_y = []
    x1, y1 = widgets["point"][0]
    x2, y2 = widgets["point"][1]
    if x1 == x2 and y1 == y2:
        ui.open_msg_window("Error message", "These points should not be the same.", error=True)
    else:
        slope, y_intercept = calculate_parameters(x1, y1, x2, y2)
        for i, x in enumerate(widgets["energy"]):
            y_new = widgets["intensity"][i] - (slope * x + y_intercept)
            new_y.append(y_new)
    return new_y
    
def draw_figure(frame):
    canvas, widgets["figure"], subplot = ui.create_figure(frame, choose_point, width=800, height=500)
    subplot.set_xlabel("Binding energy (eV)")
    subplot.set_ylabel("Intensity (arbitrary units)")
    subplot.plot(widgets["energy"], widgets["intensity"])
    
def make_belong(x, y):
    for i, energy in enumerate(widgets["energy"]):
        if energy <= x <= widgets["energy"][i+1]:
            if widgets["intensity"][i] <= y <= widgets["intensity"][i+1]:
                return i
            elif widgets["intensity"][i] >= y >= widgets["intensity"][i+1]:
                return i
            else:
                pass
        else:
            pass
            
def calculate_peak():
    xlist = []
    ylist = []
    if len(widgets["point"]) < 2:
        ui.open_msg_window("Error message", "Please choose 2 different points", error=True)
    else:
        x1, y1 = widgets["point"][-2]
        x2, y2 = widgets["point"][-1]
        index1 = make_belong(x1, y1)
        index2 = make_belong(x2, y2)
        if x1 == x2:
            ui.open_msg_window("Error message", "Please choose 2 different points", error=True)
        else:
            if x1 < x2:
                xlist = widgets["energy"][index1:index2]
                ylist = widgets["intensity"][index1:index2]
            else:
                xlist = widgets["energy"][index2:index1]
                ylist = widgets["intensity"][index2:index1]
            area = np.trapz(ylist, xlist)
            message = "The intensity of peak is {}.".format(area)
            ui.write_to_textbox(widgets["textbox"], message)
            
def save():
    """
    According to this link: https://matplotlib.org/stable/api/figure_api.html?highlight=savefig#matplotlib.figure.Figure.savefig
    """
    path = ui.open_save_dialog("Choose location to save your figure", r'C:\Users\Admin\Downloads\spectral')
    widgets["figure"].savefig(path)
    
def load():
    if len(widgets["point"]) < 2:
        ui.open_msg_window("Error message", "Please choose 2 different points", error=True)
    else:
        ui.remove_component(widgets["figureframe"])
        widgets["figureframe"] = ui.create_frame(widgets["window"], ui.TOP)
        widgets["intensity"] = only_peak()
        draw_figure(widgets["figureframe"])
        
def reset():
    ui.remove_component(widgets["figureframe"])
    widgets["figureframe"] = ui.create_frame(widgets["window"], ui.TOP)
    read_data(widgets["folderpath"])
    widgets["point"] = []
    draw_figure(widgets["figureframe"])
    
def main():
    widgets["window"] = ui.create_window("Spectral")
    widgets["figureframe"] = ui.create_frame(widgets["window"], ui.TOP)
    textframe = ui.create_frame(widgets["window"], ui.BOTTOM)
    buttonframe = ui.create_frame(textframe, ui.LEFT)
    quitbutton = ui.create_button(buttonframe, "quit", ui.quit)
    widgets["textbox"] = ui.create_textbox(textframe, width=80, height=20)
    open_folder()
    draw_figure(widgets["figureframe"])
    widgets["loadbutton"] = ui.create_button(buttonframe, "load", load)
    peakbutton = ui.create_button(buttonframe, "peak", calculate_peak)
    savebutton = ui.create_button(buttonframe, "save", save)
    resetbutton = ui.create_button(buttonframe, "reset", reset)
    ui.start()
    
if __name__ == "__main__":
    main()