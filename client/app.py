import curses
from curses import wrapper

class App:
  def __init__(self, screen):
    # Curses Library setup
    self.screen = screen
    self.window = self.screen.subwin(5, 0)
    self.window.scrollok(True)

    # Variables used in app
    self.banner = None
    self.welcome_banner = "**** Welcome to TermChat! The illest chat network on the web ****"
    self.chatrooms = None
    self.selected_chatroom = None
    self.selected_chatroom_messages = ["guest1: yo", "guest2: yo", "guest1: yo", "guest2: yo", "guest3: YOOOOOOOO"]

    # Initialize app
    self.banner = self.welcome_banner
    self.render_banner()

    self.chatrooms = self.get_chatrooms()
    self.render_waiting_lobby()

    self.prompt_lobby_input()

  def render_banner(self):
    title = self.banner
    title_len = len(title)

    # Calculate stuff for rendering title
    num_rows, num_cols = self.screen.getmaxyx()
    y_position = 0
    half_length_of_title = int(len(title) / 2)
    middle_column = int(num_cols / 2)
    x_position = middle_column - half_length_of_title

    # Calculate stuff for rendering subtitle
    subtitle = self.render_banner_subtitle_helper(title_len)

    # Calculate stuff for rendering margins
    title_margin = title_len * "*"

    self.screen.addstr(y_position + 0, x_position, title_margin)
    self.screen.addstr(y_position + 1, x_position, title)
    self.screen.addstr(y_position + 2, x_position, subtitle)
    self.screen.addstr(y_position + 3, x_position, title_margin)
    self.screen.refresh()

  def render_banner_subtitle_helper(self, message_len):
    if self.selected_chatroom == None:
      chatroom = "N/A"
    else:
      chatroom = self.selected_chatroom

    text_to_render_inner = "      Current chatroom: " + chatroom + "      "
    text_to_render_margin_len = (message_len - len(text_to_render_inner)) / 2
    text_to_render_margin_additional_len = (message_len - len(text_to_render_inner)) % 2
    text_to_render_margin_left = text_to_render_margin_len * "*"
    text_to_render_margin_right = (text_to_render_margin_len + text_to_render_margin_additional_len) * "*"
    text_to_render = text_to_render_margin_left + text_to_render_inner + text_to_render_margin_right
    return text_to_render

  def render_waiting_lobby(self):
    self.window.clear()

    self.window.addstr("Chatrooms available:\n")
    for chatroom in self.chatrooms:
      self.window.addstr("- " + chatroom + "\n")
    self.window.addstr("\n")

    self.window.refresh()

  def render_chatroom(self):
    self.window.clear()

    self.window.addstr("User has entered \"" + self.selected_chatroom + "\"\n")
    for message in self.selected_chatroom_messages:
      self.window.addstr(message + "\n")

    self.window.refresh()

  def get_chatrooms(self):
    return ["the gangsta club", "flat earthers", "dinasour gang"]

  def prompt_lobby_input(self):
    self.window.addstr("Please enter the name of the chatroom you'd like to join:\n")
    self.window.refresh()
    
    user_input = self.window.getstr()
    if user_input in set(self.chatrooms):
      self.selected_chatroom = user_input
      self.render_banner()
      self.render_chatroom()
    else:
      self.window.addstr(user_input + " is not an existing chatroom. Creating...")
      self.window.refresh()
      curses.napms(1000)
      self.selected_chatroom = user_input
      self.render_banner()
      self.render_chatroom()

    self.window.refresh()

  def print_chatroom(self):
    self.window.scroll(1)
    self.window.refresh()


def main(stdscr):
  screen = curses.initscr()
  curses.echo()

  app = App(screen)

  stdscr.getch()
  curses.endwin()

wrapper(main)

