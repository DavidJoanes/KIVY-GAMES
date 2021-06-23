from kivy import platform
from kivy.config import Config
from kivy.core.audio import SoundLoader
Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

from kivy.uix.relativelayout import RelativeLayout
import random
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.app import App
from kivy.graphics import Color, Line, Quad, Triangle
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.widget import Widget
from kivy.uix.actionbar import ActionBar
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp



Builder.load_file("home.kv")

Builder.load_string('''
<ActionBar>:
    pos_hint: {'top':1}
    ActionView:
        use_separator: True
        ActionPrevious:
            title: 'Spaceship Troopers'
            with_previous: False
        ActionOverflow:
        ActionButton:
            text: 'Btn0'
            icon: 'atlas://data/images/defaulttheme/audio-volume-high'
            
        ActionButton:
            text: 'Help'
        ActionGroup:
            text: 'Difficulty'
            ActionButton:
                text: 'Novice'
            ActionButton:
                text: 'Professional'
            ActionButton:
                text: 'Expert'
        ActionButton:
            text: 'About'
''')


class CustomActionBar(ActionBar):
    pass

class MainWidget(RelativeLayout):
    from transforms import transform, transform_2D, transform_perspective
    from userActions import keyboard_closed, on_keyboard_up, on_keyboard_down, on_touch_up, on_touch_down

    home_widget = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    vertical_NB_LINES = 8
    vertical_LINE_SPACING = 0.3  # percentage of screen width
    vertical_lines = []

    horizontal_NB_LINES = 16
    horizontal_LINE_SPACING = 0.1  # percentage of screen height
    horizontal_lines = []

    SPEED_Y = .1  # speed_y axis
    SPEED_X = 1

    current_offset_y = 0
    current_y_loop = 0

    current_speed_x = 0
    current_offset_x = 0

    number_of_tiles = 16
    tiles = []
    # tile_x = 1
    # tile_y = 3
    tiles_coordinates = []

    ship = None
    ship_width = 0.1
    ship_height = 0.035
    ship_base = 0.04
    ship_coordinates = [(0, 0), (0, 0), (0, 0)]

    game_over_state = False
    game_started_state = False
    start_game_enabled = BooleanProperty(False)
    easy_mode_enabled = BooleanProperty(True)
    medium_mode_enabled = BooleanProperty(True)
    hard_mode_enabled = BooleanProperty(True)

    home_title = StringProperty("S  P  A  C  E  S  H  I  P    T  R  O  O  P  E  R  S")
    home_button_title = StringProperty("START")

    score_text = StringProperty()
    begin_sound = None
    welcome_sound = None
    game_sound = None
    game_over_sound = None
    restart_sound = None

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        # print("Init W: " +str(self.width)+ " H: " +str(self.height))
        self.init_audio()
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()
        # self.prefill_tiles_coordinates()
        # self.generate_tiles_coordinate()
        self.reset_game()

        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)

        Clock.schedule_interval(self.update, 1/60)
        self.welcome_sound.play()

    def init_audio(self):
        self.welcome_sound = SoundLoader.load("audio/welcome.wav")
        self.begin_sound = SoundLoader.load("audio/begin.wav")
        self.game_sound = SoundLoader.load("audio/game_music.mp3")
        self.game_over_sound = SoundLoader.load("audio/game_over.wav")
        self.restart_sound = SoundLoader.load("audio/restart.wav")

        self.welcome_sound.volume = 1
        self.begin_sound.volume = .5
        self.game_sound.volume = 1
        self.game_over_sound.volume = .7
        self.restart_sound.volume = .8

    def reset_game(self):
        self.current_offset_y = 0
        self.current_y_loop = 0
        self.current_speed_x = 0
        self.current_offset_x = 0
        self.tiles_coordinates = []
        self.prefill_tiles_coordinates()
        self.generate_tiles_coordinate()
        self.score_text = "SCORE: " + str(self.current_y_loop)
        self.game_over_state = False

    def is_desktop(self):
        if platform in ("linux", "win", "macosx"):
            return True
        return False

    def init_ship(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

    def update_ship(self):
        center_x = self.width / 2
        base_y = self.ship_base * self.height
        ship_half_width = (self.ship_width * self.width) / 2
        ship_height = self.ship_height * self.height

        #   2
        # 1   3
        # self.transform
        self.ship_coordinates[0] = (center_x - ship_half_width, base_y)
        self.ship_coordinates[1] = (center_x, base_y + ship_height)
        self.ship_coordinates[2] = (center_x + ship_half_width, base_y)

        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])
        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def check_ship_collision(self):
        for x in range(0, len(self.tiles_coordinates)):
            tile_x, tile_y = self.tiles_coordinates[x]
            if tile_y > self.current_y_loop + 1:
                return False
            if self.check_for_collision_with_tile(tile_x, tile_y):
                return True
        return False

    def check_for_collision_with_tile(self, tile_x, tile_y):
        xmin, ymin = self.get_tile_coordinates(tile_x, tile_y)
        xmax, ymax = self.get_tile_coordinates(tile_x + 1, tile_y + 1)
        for x in range(0, 3):
            point_x, point_y = self.ship_coordinates[x]
            if xmin <= point_x <= xmax and ymin <= point_y <= ymax:
                return True
        return False

    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for x in range(0, self.number_of_tiles):
                self.tiles.append(Quad())

    def prefill_tiles_coordinates(self):
        for x in range(0, 10):
            self.tiles_coordinates.append((0, x))

    def generate_tiles_coordinate(self):
        last_value_of_x = 0
        last_value_of_y = 0
        # clean the coordinates that are out of the screen
        # tile_y < self.current_y_loop
        for x in range(len(self.tiles_coordinates)-1, -1, -1):
            if self.tiles_coordinates[x][1] < self.current_y_loop:
                del self.tiles_coordinates[x]

        if len(self.tiles_coordinates) > 0:
            last_coordinates = self.tiles_coordinates[-1]
            last_value_of_x = last_coordinates[0]
            last_value_of_y = last_coordinates[1] + 1
        print("a")

        for x in range(len(self.tiles_coordinates), self.number_of_tiles):
            random_value = random.randint(0, 2)
            # 0 -> straight
            # 1 -> right
            # 2 -> left

            start_index = -int(self.vertical_NB_LINES / 2) + 1
            end_index = start_index + self.vertical_NB_LINES - 2

            if last_value_of_x <= start_index:
                random_value = 1
            if last_value_of_x >= end_index:
                random_value = 2

            self.tiles_coordinates.append((last_value_of_x, last_value_of_y))
            if random_value == 1:
                last_value_of_x += 1
                self.tiles_coordinates.append((last_value_of_x, last_value_of_y))
                last_value_of_y += 1
                self.tiles_coordinates.append((last_value_of_x, last_value_of_y))
            if random_value == 2:
                last_value_of_x -= 1
                self.tiles_coordinates.append((last_value_of_x, last_value_of_y))
                last_value_of_y += 1
                self.tiles_coordinates.append((last_value_of_x, last_value_of_y))

            last_value_of_y += 1
        print("b")

    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            # self.line = Line(points=[100, 0, 100, 100])
            for x in range(0, self.vertical_NB_LINES):
                self.vertical_lines.append(Line())

    def get_lineX_from_index(self, index):
        central_line_x = self.perspective_point_x
        spacing = self.vertical_LINE_SPACING * self.width
        offset = index - 0.5
        line_x = central_line_x + (offset * spacing + self.current_offset_x)
        return line_x

    def get_lineY_from_index(self, index):
        spacing_y = self.horizontal_LINE_SPACING * self.height
        line_y = index * spacing_y - self.current_offset_y
        return line_y

    def get_tile_coordinates(self, tile_x, tile_y):
        tile_y = tile_y - self.current_y_loop
        x = self.get_lineX_from_index(tile_x)
        y = self.get_lineY_from_index(tile_y)
        return x, y

    def update_tiles(self):
        for x in range(0, self.number_of_tiles):
            tile = self.tiles[x]
            tile_coordinates = self.tiles_coordinates[x]
            xmin, ymin = self.get_tile_coordinates(tile_coordinates[0], tile_coordinates[1])
            xmax, ymax = self.get_tile_coordinates(tile_coordinates[0]+1, tile_coordinates[1]+1)

            # 2 3
            #
            # 1 4
            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)

            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update_vertical_lines(self):
        # -1 0 1 2
        start_index = -int(self.vertical_NB_LINES / 2) + 1
        for x in range(start_index, start_index + self.vertical_NB_LINES):
            line_x = self.get_lineX_from_index(x)

            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[x].points = [x1, y1, x2, y2]

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for x in range(0, self.horizontal_NB_LINES):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self):
        start_index = -int(self.vertical_NB_LINES / 2) + 1
        end_index = (start_index + self.vertical_NB_LINES) - 1

        xmin = self.get_lineX_from_index(start_index)
        xmax = self.get_lineX_from_index(end_index)

        for x in range(0, self.horizontal_NB_LINES):
            line_y = self.get_lineY_from_index(x)

            x1, y1 = self.transform(xmin, line_y)
            x2, y2 = self.transform(xmax, line_y)
            self.horizontal_lines[x].points = [x1, y1, x2, y2]


    def update(self, dt):
        # print("update")
        # print("dt: "+str(dt*60))
        time_factor = dt*60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()

        if not self.game_over_state and self.game_started_state:
            speed_y = (self.SPEED_Y * self.height) / 100
            self.current_offset_y += (speed_y * time_factor)

            spacing_y = self.horizontal_LINE_SPACING * self.height
            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1
                self.score_text = "SCORE: " + str(self.current_y_loop)
                self.generate_tiles_coordinate()
                if self.easy_mode:
                    self.SPEED_Y += 0.05
                    if self.current_y_loop >= 5:
                        self.SPEED_Y = .1
                    elif self.current_y_loop >= 20:
                        self.SPEED_Y = .2
                    elif self.current_y_loop >= 40:
                        self.SPEED_Y = .4
                    elif self.current_y_loop >= 60:
                        self.SPEED_Y = .6
                    elif self.current_y_loop >= 80:
                        self.SPEED_Y = .8
                    elif self.current_y_loop >= 100:
                        self.SPEED_Y = 1
                    elif self.current_y_loop >= 150:
                        self.SPEED_Y = 1.3
                    elif self.current_y_loop >= 200:
                        self.SPEED_Y = 1.6
                    elif self.current_y_loop >= 250:
                        self.SPEED_Y = 1.8
                    elif self.current_y_loop >= 300:
                        self.SPEED_Y = 2
                    elif self.current_y_loop >= 350:
                        self.SPEED_Y = 2.3
                    elif self.current_y_loop >= 400:
                        self.SPEED_Y = 2.6
                    elif self.current_y_loop >= 550:
                        self.SPEED_Y = 2.9
                    elif self.current_y_loop >= 650:
                        self.SPEED_Y = 3.1
                    elif self.current_y_loop >= 750:
                        self.SPEED_Y = 3.5
                    elif self.current_y_loop >= 850:
                        self.SPEED_Y = 3.7
                    elif self.current_y_loop >= 950:
                        self.SPEED_Y = 3.9
                    elif self.current_y_loop >= 1050:
                        self.SPEED_Y = 4.1
                if self.medium_mode:
                    self.SPEED_Y = .1
                    if self.current_y_loop >= 5:
                        self.SPEED_Y = .3
                    elif self.current_y_loop >= 20:
                        self.SPEED_Y = .6
                    elif self.current_y_loop >= 40:
                        self.SPEED_Y = .9
                    elif self.current_y_loop >= 60:
                        self.SPEED_Y = 1.2
                    elif self.current_y_loop >= 80:
                        self.SPEED_Y = 1.5
                    elif self.current_y_loop >= 100:
                        self.SPEED_Y = 1.8
                    elif self.current_y_loop >= 150:
                        self.SPEED_Y = 2.1
                    elif self.current_y_loop >= 200:
                        self.SPEED_Y = 2.4
                    elif self.current_y_loop >= 250:
                        self.SPEED_Y = 2.7
                    elif self.current_y_loop >= 300:
                        self.SPEED_Y = 3
                    elif self.current_y_loop >= 350:
                        self.SPEED_Y = 3.3
                    elif self.current_y_loop >= 400:
                        self.SPEED_Y = 3.6
                    elif self.current_y_loop >= 550:
                        self.SPEED_Y = 3.9
                    elif self.current_y_loop >= 650:
                        self.SPEED_Y = 4.2
                    elif self.current_y_loop >= 750:
                        self.SPEED_Y = 4.5
                    elif self.current_y_loop >= 850:
                        self.SPEED_Y = 4.8
                    elif self.current_y_loop >= 950:
                        self.SPEED_Y = 5.2
                    elif self.current_y_loop >= 1050:
                        self.SPEED_Y = 5.5
                if self.hard_mode:
                    # while self.current_y_loop:
                    #     self.SPEED_Y += 0.00000000000001
                    # print(self.SPEED_Y)
                    self.SPEED_Y = .25
                    if self.current_y_loop >= 5:
                        self.SPEED_Y = .5
                    elif self.current_y_loop >= 20:
                        self.SPEED_Y = 1
                    elif self.current_y_loop >= 40:
                        self.SPEED_Y = 1.5
                    elif self.current_y_loop >= 60:
                        self.SPEED_Y = 2
                    elif self.current_y_loop >= 80:
                        self.SPEED_Y = 2.5
                    elif self.current_y_loop >= 100:
                        self.SPEED_Y = 3
                    elif self.current_y_loop >= 150:
                        self.SPEED_Y = 3.5
                    elif self.current_y_loop >= 250:
                        self.SPEED_Y = 4
                    elif self.current_y_loop >= 350:
                        self.SPEED_Y = 4.5
                    elif self.current_y_loop >= 450:
                        self.SPEED_Y = 5
                    elif self.current_y_loop >= 550:
                        self.SPEED_Y = 5.5
                    elif self.current_y_loop >= 650:
                        self.SPEED_Y = 6
                    elif self.current_y_loop >= 750:
                        self.SPEED_Y = 7
                    elif self.current_y_loop >= 850:
                        self.SPEED_Y = 8
                    elif self.current_y_loop >= 950:
                        self.SPEED_Y = 9
                    elif self.current_y_loop >= 1000:
                        self.SPEED_Y = 10
                    elif self.current_y_loop >= 1200:
                        self.SPEED_Y = 12


            speed_x = (self.current_speed_x * self.width) / 100
            self.current_offset_x += (speed_x * time_factor)

        if not self.check_ship_collision() and not self.game_over_state:
            self.game_over_state = True
            self.home_title = "G A M E  O V E R !"
            self.home_button_title = "RESTART"
            self.home_widget.opacity = 1
            self.game_sound.stop()
            self.game_over_sound.play()
            # Clock.schedule_once(self.play_game_over_sound, 3)
            print("GAME OVER!")

    # def play_game_over_sound(self, dt):
    #     self.game_over_sound.play()

    # def continue_playing_game_sound(self, dt):
    #     if not self.game_over_state:
    #         self.game_sound.play()

    def game_started(self):
        # print("Button")
        if self.game_over_state:
            self.restart_sound.play()
            self.game_sound.play()
            # Clock.schedule_once(self.continue_playing_game_sound, 2)
        else:
            self.game_sound.play()
        self.reset_game()
        self.game_started_state = True
        self.home_widget.opacity = 0

    def easy_mode(self, widget):
        # print("Toggle button " + widget.state)
        if widget.state == "normal":
            widget.text = "Easy"
            self.start_game_enabled = False
            self.medium_mode_enabled = True
            self.hard_mode_enabled = True
        else:
            widget.text = "EASY"
            self.start_game_enabled = True
            self.medium_mode_enabled = False
            self.hard_mode_enabled = False

    def medium_mode(self, widget):
        # print("Toggle button " + widget.state)
        if widget.state == "normal":
            widget.text = "Medium"
            self.start_game_enabled = False
            self.easy_mode_enabled = True
            self.hard_mode_enabled = True
        else:
            widget.text = "MEDIUM"
            self.start_game_enabled = True
            self.easy_mode_enabled = False
            self.hard_mode_enabled = False

    def hard_mode(self, widget):
        # print("Toggle button " + widget.state)
        if widget.state == "normal":
            widget.text = "Hard"
            self.start_game_enabled = False
            self.easy_mode_enabled = True
            self.medium_mode_enabled = True
        else:
            widget.text = "HARD"
            self.start_game_enabled = True
            self.easy_mode_enabled = False
            self.medium_mode_enabled = False

class Spaceship_Troopers(App):
    def build(self):
        self.title = "Spaceship Troopers"
        # return CustomActionBar()

    # def menu_button(self):
    #     print("clicked")
    pass


if __name__ == "__main__":
    Spaceship_Troopers().run()