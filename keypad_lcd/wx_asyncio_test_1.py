"""
Test wxPython/Phoenix application with asyncio module
===========================================================

Creates a dialog with 4 gauges.

    * Gauge 1 is updated every 100ms by a wxTimer.
    * Gauge 2 is updated every 200ms by an asyncio coroutine/task.
    * Gauge 3 is updated every 300ms by an asyncio coroutine/task.
    * Gauge 4 is updated every 400ms by an asyncio coroutine/task.

The main app calls the `idle_handler` to run a single iteration of the asyncio
event loop.

If the `idle_handler` requests more idle events immediately the guages update
as expected, however the CPU load is high (~100%).

Using a wxTimer with 1ms inverval to call the asyncio event loop seems to work
well and keeps the CPU load (~2-3%).
"""

import wx
import wx.lib.sized_controls as wxSC

import asyncio

##============================================================================

class MyDialog(wxSC.SizedDialog):
    def __init__(self, parent, id):
        wxSC.SizedDialog.__init__(self, None, wx.ID_ANY, "SizedForm Dialog",
                        style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        pane = self.GetContentsPane()
        pane.SetSizerType("form")

        self.count1 = 0
        self.count2 = 0
        self.count3 = 0
        self.count4 = 0

        max = self.count_max = 40
        size = (250, -1)

        ## Row 1
        wx.StaticText(pane, label="Gauge 1")
        self.gauge1 = wx.Gauge(pane, range=max, size=size)

        ## Row 2
        wx.StaticText(pane, label="Gauge 2")
        self.gauge2 = wx.Gauge(pane, range=max, size=size)

        ## Row 3
        wx.StaticText(pane, label="Gauge 3")
        self.gauge3 = wx.Gauge(pane, range=max, size=size)

        ## Row 4
        wx.StaticText(pane, label="Gauge 4")
        self.gauge4 = wx.Gauge(pane, range=max, size=size)

        ## add dialog buttons
        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))

        ## ensure can't resize dialog to less screen space than the controls need
        self.Fit()
        self.SetMinSize(self.GetSize())

        ## bind timer event to a timer handler (to update gauge 1)
        self.Bind(wx.EVT_TIMER, self.timer_handler)
        self.timer = wx.Timer(self)
        self.timer.Start(100)

        ## Get a handle to the asyncio event loop.
        loop = asyncio.get_event_loop()

        ## Add asyncio tasks to udate gauages 2-4.
        loop.create_task( self.update_gauge2_task() )
        loop.create_task( self.update_gauge3_task() )
        loop.create_task( self.update_gauge4_task() )

    def __del__(self):
        self.timer.Stop()

    def timer_handler(self, event):
        """TimerHandler updates gauge1."""
        #print("timer_handler:")
        self.count1 = 0 if self.count1 >= self.count_max else self.count1 + 1
        self.gauge1.SetValue(self.count1)

    async def update_gauge2_task(self):
        """Asynchronous function/task to update gauge2."""
        while True:
            #print("update_gauge2_task:")
            self.count2 = 0 if self.count2 >= self.count_max else self.count2 + 1
            self.gauge2.SetValue(self.count2)
            #await asyncio.sleep_ms(200);
            await asyncio.sleep(100/1000);      ## 100ms

    async def update_gauge3_task(self):
        """Asynchronous function/task to update gauge3."""
        while True:
            #print("update_gauge3_task:")
            self.count3 = 0 if self.count3 >= self.count_max else self.count3 + 1
            self.gauge3.SetValue(self.count3)
            await asyncio.sleep(200/1000);      ## 200ms

    async def update_gauge4_task(self):
        """Asynchronous function/task to update gauge4."""
        while True:
            #print("update_gauge4_task:")
            self.count4 = 0 if self.count4 >= self.count_max else self.count4 + 1
            self.gauge4.SetValue(self.count4)
            await asyncio.sleep(300/1000);      ## 300ms

##============================================================================

class MyApp(wx.App):
    def __init__(self):
        wx.App.__init__(self, False)

        ## Only specified windows will receive the idle event, not all windows.
        wx.IdleEvent.SetMode(wx.IDLE_PROCESS_SPECIFIED)

        ## bind idle event run the asyncio event loop.
        self.Bind(wx.EVT_IDLE, self.idle_handler)

        self.timer = wx.Timer(self)
        self.timer.Start(1)

        ## bind timer event handler (to run asyncio loop).
        self.Bind(wx.EVT_TIMER, self.idle_handler)

        ## Get a handle to the asyncio event loop.
        loop = self.asyncio_loop = asyncio.get_event_loop()

    def __del__(self):
        self.timer.Stop()

    def idle_handler(self, event):
        """Idle handler runs the asyncio event loop."""
        #print("idel_handler: MyApp")

        ## Run the asyncio loop for once until all events handled (i.e. not forever).
        #self.asyncio_loop._run_once()
        self.asyncio_loop.call_soon(self.asyncio_loop.stop) ; self.asyncio_loop.run_forever()

        ## Force another idle event to be generated even if no wx events have occurred (note: high cpu usage !!)
        #event.RequestMore(True)

def main():
    """Show the main form."""
    app = MyApp()
    dlg = MyDialog(None, id=wx.ID_ANY)
    dlg.CenterOnScreen()
    dlg.ShowModal()
    dlg.Destroy()

##============================================================================

if __name__ == '__main__':
    main()

