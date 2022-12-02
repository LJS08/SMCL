import wx


class Advanced_Settings(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Advanced Setting", size=(400, 300))
        panel = wx.Panel(parent=self)
        self.statictext0 = wx.StaticText(parent=panel, label="此为开发者内部功能.")
        self.statictext1 = wx.StaticText(parent=panel, label="版本号Alpha v0.0.1.")

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        hbox.Add(self.statictext0, proportion=0, flag=wx.LEFT)
        #  | wx.ALL | wx.FIXED_MINSIZE
        hbox.Add(self.statictext1, proportion=0, flag=wx.RIGHT)

        vbox_main = wx.BoxSizer(wx.VERTICAL)

        vbox_main.Add(hbox, proportion=0, flag=wx.BOTTOM)
        # flag=wx.ALIGN_CENTRE_HORIZONTAL | wx.FIXED_MINSIZE | wx.TOP
        panel.SetSizer(vbox_main)



