import curses
from curses import wrapper

# class AppState(Enum):
#   WELCOME = 1
#   CHAT = 2

class App:
  def __init__(self, screen):
    self.screen = screen

  def print_headline(self, message):
    num_rows, num_cols = self.screen.getmaxyx()
    y_position = 0

    half_length_of_message = int(len(message) / 2)
    middle_column = int(num_cols / 2)
    x_position = middle_column - half_length_of_message

    message_margin = len(message) * "*"

    self.screen.addstr(y_position + 0, x_position, message_margin)
    self.screen.addstr(y_position + 1, x_position, message)
    self.screen.addstr(y_position + 2, x_position, message_margin)
    self.screen.addstr("\n\n")
    self.screen.refresh()

  def print_chatrooms_list(self, chatrooms):
    self.screen.addstr("Chatrooms available:\n")

    for chatroom in chatrooms:
      self.screen.addstr("- " + chatroom + "\n")

    self.screen.addstr("\n")
    self.screen.refresh()

  def input_subscribe_chatroom(self):
    self.screen.addstr("Please enter the name of the chatroom you'd like to join:\n")
    self.screen.refresh()
    
    self.user_input = self.screen.getstr()
    self.screen.addstr("You selected: \"" + self.user_input + "\"\n")
    self.screen.refresh()

  def batch_get_chatrooms(self):
    return ["gangsta club", "flat earthers", "dinasour gang"]


def main(stdscr):
  screen = curses.initscr()
  curses.echo()

  app = App(screen)

  app.print_headline("**** Welcome to TermChat! The illest chat network on the web ****")

  chatrooms = app.batch_get_chatrooms()
  app.print_chatrooms_list(chatrooms)

  app.input_subscribe_chatroom()

  stdscr.getch()
  curses.endwin()

wrapper(main)

