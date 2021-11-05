import wx.adv
import wx
import threading
import time
import requests
import webbrowser
import os

TRAY_TOOLTIP = 'Name'
TRAY_ICON_OPEN = 'img/open_door.png'
TRAY_ICON_CLOSED = 'img/closed_door.png'

dirname = os.path.dirname(__file__)
TRAY_ICON_OPEN = os.path.join(dirname, TRAY_ICON_OPEN)
TRAY_ICON_CLOSED = os.path.join(dirname, TRAY_ICON_CLOSED)

URL = "https://labor.bit-bots.de"

EVT_RESULT_ID = int(wx.NewIdRef())


class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        self.frame = frame
        super(TaskBarIcon, self).__init__()
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def _create_menu_item(self, menu, label, func):
        item = wx.MenuItem(menu, -1, label)
        menu.Bind(wx.EVT_MENU, func, id=item.GetId())
        menu.Append(item)
        return item

    def CreatePopupMenu(self):
        menu = wx.Menu()
        self._create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_door_icon_open(self):
        icon = wx.Icon(TRAY_ICON_OPEN)
        self.SetIcon(icon, TRAY_TOOLTIP)

    def set_door_icon_closed(self):
        icon = wx.Icon(TRAY_ICON_CLOSED)
        self.SetIcon(icon, TRAY_TOOLTIP)

    def on_left_down(self, event):
        webbrowser.open(URL)

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)
        self.frame.Close()


def EVT_RESULT(win, func):
     """Define Result Event."""
     win.Connect(-1, -1, EVT_RESULT_ID, func)

class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

class App(wx.App):
    def OnInit(self):
        frame=wx.Frame(None)
        self.SetTopWindow(frame)
        self.icon = TaskBarIcon(frame)
        EVT_RESULT(self,self.OnResult)
        return True

    def OnResult(self, event):
        if event.data:
            self.icon.set_door_icon_open()
        else:
            self.icon.set_door_icon_closed()

def set_data(app):
    while True:
        try:
            req = requests.get(URL, headers= {"content-type": "application/json"})
            print(req.status_code)
            if req.status_code == 200:
                data = req.json()
                print(data)
                if data['available']:
                    wx.PostEvent(app, ResultEvent(data['open']))
                else:
                    print("Sensor down")
        except Exception as e:
            print(e)
            pass
        time.sleep(30)


if __name__ == '__main__':
    app = App(False)
    thread = threading.Thread(target=set_data, args=(app,))
    thread.setDaemon(True)
    thread.start()
    app.MainLoop()
    thread.stop()
