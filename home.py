from tkinter import Label, Button

from kivy.app import App
from kivy.uix.pagelayout import PageLayout
from kivy.uix.relativelayout import RelativeLayout


class HomeWidget(RelativeLayout):
    def on_touch_down(self, touch):
        if self.opacity == 0:
            return False
        return super(RelativeLayout, self).on_touch_down(touch)

# class HomeMenu(App):
#     def build(self):
#         return HomeWidget()
#
# # if __name__ == "__main__":
# HomeWidget()