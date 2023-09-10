import json
import os
import re
import wx

class Frame(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent=None, title=title, style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_panel = wx.Panel(self)
        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        timer_select_sizer = wx.BoxSizer()
        timer_label_sizer = wx.GridBagSizer(hgap=15)
        buttons_sizer = wx.BoxSizer()

        self.med_font = wx.Font()
        self.med_font.SetPointSize(14)
        self.large_font = wx.Font()
        self.large_font.SetPointSize(40)

        self.current_timer = None
        self.session_time = 0
        self.total_time = 0

        self.timer = wx.Timer(self)
        # The Frame itself is binded to the timer event, not the timer itself.
        self.Bind(wx.EVT_TIMER,self.on_timer,self.timer)

        # Load configuration and unset self.current_timer if it does not exist.
        if os.path.exists('times.json'):
            with open('times.json', 'r') as f:
                self.config = json.load(f)
                self.config["times"] = dict(sorted(self.config["times"].items()))
        else:
            self.config = {"last_timer":"","times":{}}

        # Timer selection controls.
        self.timer_dropdown = wx.ComboBox(main_panel, choices=list(self.config["times"].keys()))
        self.timer_dropdown.SetMinSize((160,-1))
        self.timer_dropdown.Bind(wx.EVT_COMBOBOX, self.on_select)
        self.add_button = wx.Button(main_panel,label="Add")
        self.add_button.Bind(wx.EVT_BUTTON,self.on_add_button)
        self.rename_button = wx.Button(main_panel,label="Rename")
        self.rename_button.Bind(wx.EVT_BUTTON,self.on_rename_button)
        self.delete_button = wx.Button(main_panel,label="Delete")
        self.delete_button.Bind(wx.EVT_BUTTON,self.on_delete_button)
        if self.config["last_timer"] == "":
            self.current_timer = None
            self.delete_button.Disable()
        else:
            self.current_timer = self.config["last_timer"]
            self.timer_dropdown.Select(self.timer_dropdown.FindString(self.current_timer))

        # Timer texts.
        self.session_time_label = wx.StaticText(main_panel,label="Session")
        self.session_time_label.SetFont(self.med_font)
        self.session_time_text = wx.StaticText(main_panel,label=self.time_string(self.session_time))
        self.session_time_text.SetFont(self.large_font)
        self.total_time_label = wx.StaticText(main_panel,label="Total")
        self.total_time_label.SetFont(self.med_font)
        self.total_time_text = wx.StaticText(main_panel,label=self.time_string(self.total_time))
        self.total_time_text.SetFont(self.large_font)
        self.load_time()
        self.write_time()

        # Timer control buttons.
        self.start_button = wx.Button(main_panel,label="Start")
        self.start_button.Bind(wx.EVT_BUTTON,self.on_start_button)
        self.change_time_button = wx.Button(main_panel,label="Change Time")
        self.change_time_button.Bind(wx.EVT_BUTTON,self.on_change_time_button)
        self.reset_button = wx.Button(main_panel,label="Reset")
        self.reset_button.Bind(wx.EVT_BUTTON,self.on_reset_button)
        if self.current_timer is None:
            self.start_button.Disable()
            self.change_time_button.Disable()
            self.reset_button.Disable()
        else:
            self.start_button.Enable()
            self.change_time_button.Enable()
            self.reset_button.Enable()

        timer_select_sizer.Add(self.timer_dropdown,0)
        timer_select_sizer.Add(self.add_button,0)
        timer_select_sizer.Add(self.rename_button,0)
        timer_select_sizer.Add(self.delete_button,0)
        timer_label_sizer.Add(self.session_time_label,wx.GBPosition(0,0),flag=wx.EXPAND | wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        timer_label_sizer.Add(self.session_time_text,wx.GBPosition(0,1),flag=wx.EXPAND)
        timer_label_sizer.Add(self.total_time_label,wx.GBPosition(1,0),flag=wx.EXPAND | wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        timer_label_sizer.Add(self.total_time_text,wx.GBPosition(1,1),flag=wx.EXPAND)
        timer_label_sizer.Add((0,0),wx.GBPosition(0,2),flag=wx.EXPAND,span=wx.GBSpan(2,1))
        timer_label_sizer.AddGrowableCol(2)
        buttons_sizer.Add(self.start_button,1)
        buttons_sizer.Add(self.change_time_button,1)
        buttons_sizer.Add(self.reset_button,1)

        panel_sizer.Add(timer_select_sizer,0,wx.ALL,border=5)
        panel_sizer.Add(timer_label_sizer,0,wx.CENTER,border=5)
        panel_sizer.Add(buttons_sizer,0,wx.EXPAND | wx.ALL,border=5)

        main_panel.SetSizer(panel_sizer)
        main_sizer.Add(main_panel,1,wx.EXPAND)
        self.SetSizerAndFit(main_sizer)

        self.Bind(wx.EVT_CLOSE,self.on_exit)

    def time_string(self,time):
        hours = time // 3600
        minutes = (time % 3600) // 60
        seconds = time % 60

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def check_time_string(self,time_string):
        """Validate time string input and return the sum in seconds."""

        pattern = r'^\d{1,}:[0-5][0-9]:[0-5][0-9]$'
        if re.match(pattern, time_string):
            seconds = int(time_string[-2::1])
            minutes = int(time_string[-5:-3]) * 60
            hours = int(time_string[0:-6]) * 3600

            return hours + minutes + seconds
        else:
            return None

    def load_time(self):
        self.session_time = 0
        self.total_time = self.config["times"].get(self.current_timer,0)
        self.update_times()

    def delete_key_get_previous(self, d: dict, key):
        """Delete a key from a dictionary and return the previous key.
        Returns None if there was only one key in the dictionary."""

        keys = list(d.keys())
        if key in keys:
            index = keys.index(key)
            del d[key]
            if index > 0:
                return keys[index - 1]
            elif index == 0 and len(keys) > 1:
                return keys[1]
        return None

    def write_time(self):
        with open("time.txt","w") as txt:
            txt.write(f"{self.time_string(self.session_time)}\n{self.time_string(self.total_time)}")

    def update_times(self):
        self.session_time_text.SetLabel(self.time_string(self.session_time))
        self.total_time_text.SetLabel(self.time_string(self.total_time))

    def on_select(self,event):
        self.current_timer = self.timer_dropdown.GetValue()
        self.load_time()
        self.write_time()
        self.start_button.Enable()
        self.change_time_button.Enable()
        self.reset_button.Enable()

    def on_add_button(self,event):
        # Form new timer name.
        timer_names = self.config["times"].keys()
        timer_num = 1
        while (new_default := "Timer" + str(timer_num)) in timer_names:
            timer_num += 1

        with wx.TextEntryDialog(self,"New timer name:",value=new_default) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                name = dialog.GetValue()
                if name != "" and name not in self.config["times"].keys():
                    self.current_timer = name
                    self.config["times"][name] = 0
                    self.config["times"] = dict(sorted(self.config["times"].items()))
                    self.timer_dropdown.Clear()
                    self.timer_dropdown.AppendItems(list(self.config["times"].keys()))
                    self.timer_dropdown.Select(self.timer_dropdown.FindString(self.current_timer))
                    self.delete_button.Enable()
                    self.start_button.Enable()
                    self.change_time_button.Enable()
                    self.reset_button.Enable()
                    self.session_time = 0
                    self.total_time = 0
                    self.write_time()
                    self.update_times()

    def on_rename_button(self,event):
        with wx.TextEntryDialog(self,"New timer name:",value=self.current_timer) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                name = dialog.GetValue()
                if name != "":
                    if name in self.config["times"].keys():
                        error = wx.MessageDialog(self,"New timer name already exists.",caption="Error Renaming Timer",style=wx.ICON_WARNING)
                        error.ShowModal()
                        error.Destroy()
                    else:
                        self.config["times"][name] = self.config["times"].pop(self.current_timer)
                        self.config["times"] = dict(sorted(self.config["times"].items()))
                        self.current_timer = name
                        self.timer_dropdown.Clear()
                        self.timer_dropdown.AppendItems(list(self.config["times"].keys()))
                        self.timer_dropdown.Select(self.timer_dropdown.FindString(self.current_timer))

    def on_delete_button(self,event):
        with wx.MessageDialog(self,f"Delete timer {self.current_timer}?",style=wx.YES_NO) as dialog:
            if dialog.ShowModal() == wx.ID_YES:
                prev_timer = self.delete_key_get_previous(self.config["times"],self.current_timer)
                self.timer_dropdown.Delete(self.timer_dropdown.GetSelection())
                if prev_timer is not None:
                    self.timer_dropdown.SetSelection(self.timer_dropdown.FindString(prev_timer))
                    self.current_timer = self.timer_dropdown.GetValue()
                    self.session_time = 0
                    self.load_time()
                    self.write_time()
                else:
                    self.current_timer = None
                    self.session_time = 0
                    self.total_time = 0
                    self.update_times()
                    self.timer_dropdown.SetValue("")
                    self.delete_button.Disable()
                    self.start_button.Disable()
                    self.change_time_button.Disable()
                    self.reset_button.Disable()

    def on_timer(self,event):
        self.session_time += 1
        self.total_time += 1
        self.config["times"][self.current_timer] = self.total_time
        self.write_time()
        self.update_times()

    def on_start_button(self,event):
        self.update_times()
        label = self.start_button.GetLabel()
        if label == "Start":
            self.timer.Start(1000)
            self.start_button.SetLabel("Stop")
            self.change_time_button.Disable()
            self.reset_button.Disable()
            self.timer_dropdown.Disable()
            self.add_button.Disable()
            self.rename_button.Disable()
            self.delete_button.Disable()
        else:
            self.timer.Stop()
            self.start_button.SetLabel("Start")
            self.change_time_button.Enable()
            self.reset_button.Enable()
            self.timer_dropdown.Enable()
            self.add_button.Enable()
            self.rename_button.Enable()
            self.delete_button.Enable()

    def on_change_time_button(self,event):
        with wx.TextEntryDialog(self,"Edit total time value:",value=self.time_string(self.total_time)) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                new_time = self.check_time_string(dialog.GetValue())
                if new_time is not None:
                    self.config["times"][self.current_timer] = new_time
                    self.total_time = new_time
                    self.write_time()
                    self.update_times()
                else:
                    error = wx.MessageDialog(self,"Invalid time input.",caption="Error Editing Timer",style=wx.ICON_WARNING)
                    error.ShowModal()
                    error.Destroy()

    def on_reset_button(self,event):
        self.session_time = 0
        self.total_time = 0
        self.session_time_text.SetLabel(self.time_string(0))
        self.total_time_text.SetLabel(self.time_string(0))

    def on_exit(self,event):
        self.config["last_timer"] = (self.current_timer if self.current_timer is not None else "")
        with open("times.json","w") as config:
            config.write(json.dumps(self.config,indent=4))
        with open("time.txt","w") as time:
            time.write("--:--:--\n--:--:--")
        event.Skip()


if __name__ == '__main__':
    app = wx.App()
    frame = Frame(None, title="Mr. Stopwatch")
    frame.Show()
    app.MainLoop()