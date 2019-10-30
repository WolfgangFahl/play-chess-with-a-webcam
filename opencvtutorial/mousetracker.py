#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from kivy.app import App
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout


class TrackerScreen(GridLayout):

    def __init__(self, **kwargs):
        super(TrackerScreen, self).__init__(**kwargs)
        self.cols = 2
        self.mouseLabel = self.addLabel("MousePos:")
        Window.bind(mouse_pos=lambda w, p: setattr(self.mouseLabel, 'text', str(p) + "(" + str(Window.left) + "," + str(Window.top) + ")" + str(Window.size)))

    def addLabel(self, title):
        newLabel = Label()
        self.add_widget(Label(text=title))
        self.add_widget(newLabel)
        return newLabel


class MousePos(App):

    def build(self):
        return TrackerScreen()


if __name__ == '__main__':
    MousePos().run()
