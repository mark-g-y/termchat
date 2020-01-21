import curses
from curses import wrapper
import json 
import time
import socket                
import threading 

class App:
  def __init__(self, screen):
    # Curses Library setup
    self.screen = screen
    self.window = self.screen.subwin(5, 0)
    self.window.scrollok(True)

    # Socket Library setup
    port = 1738
    self.socket = socket.socket()
    self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) 
    self.socket.connect(('44.229.87.232', port))
    self.reader, self.writer = self.socket.makefile('r'), self.socket.makefile('w')

    # Variables used in app
    self.banner = None
    self.welcome_banner = "**** Welcome to TermChat! The illest chat network on the web ****"
    self.chatrooms = None
    self.selected_chatroom = None
    self.selected_chatroom_messages = None
    # self.selected_chatroom_messages = ["guest1: yo", "guest2: yo", "guest1: yo", "guest2: yo", "guest3: YOOOOOOOO"]

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
    subtitle = self.get_banner_subtitle(title_len)

    # Calculate stuff for rendering margins
    title_margin = title_len * "*"

    self.screen.addstr(y_position + 0, x_position, title_margin)
    self.screen.addstr(y_position + 1, x_position, title)
    self.screen.addstr(y_position + 2, x_position, subtitle)
    self.screen.addstr(y_position + 3, x_position, title_margin)
    self.screen.refresh()

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
    if self.selected_chatroom_messages != None:
      for message in self.selected_chatroom_messages:
        self.window.addstr(message + "\n")

    self.window.refresh()

    t1 = threading.Thread(target = self.update_chatroom_thread)
    t1.start()

    # t2 = threading.Thread(target = self.prompt_chatroom_input)
    # t2.start()

    self.prompt_chatroom_input()

  def get_banner_subtitle(self, message_len):
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

  def get_chatrooms(self):
    self.reader.write(json.dumps({'type': 'list_chatrooms'}) + '\n')
    self.reader.flush()
    chatrooms_reponse = json.loads(self.socket.recv(1024))
    return chatrooms_reponse["chatroom_ids"]

  def prompt_lobby_input(self):
    self.window.addstr("Please enter the name of the chatroom you'd like to join:\n")
    self.window.refresh()
    
    user_input = self.window.getstr()
    if user_input not in set(self.chatrooms):
      self.window.addstr(user_input + " is not an existing chatroom. Creating...")
      self.window.refresh()

    self.selected_chatroom = user_input
    self.writer.write(json.dumps({'type': 'subscribe', 'chatroom_id': self.selected_chatroom}) + '\n')
    self.writer.flush()

    self.render_banner()
    self.render_chatroom()
    self.window.refresh()

  def prompt_chatroom_input(self):
    num_rows, num_cols = self.screen.getmaxyx()
    input = self.screen.subwin(num_rows - 1, 0)
    input.clear()
    input.addstr("> ")
    input.refresh()

    user_input = input.getstr()
    self.writer.write(json.dumps({'type': 'message', 'text': user_input}) + '\n')
    self.writer.flush()
    self.prompt_chatroom_input()

  def update_chatroom_thread(self):
    self.window.refresh()

    resp = self.reader.readline()
    # self.window.addstr(resp)
    if json.loads(resp)["type"] != "ping":
      chatroom_message_reponse = json.loads(resp)
      self.window.addstr("guest: " + chatroom_message_reponse["text"] + '\n')
      self.window.refresh()

    self.update_chatroom_thread()

  def scroll_chatroom(self):
    self.window.scroll(1)
    self.window.refresh()

def main(stdscr):
  screen = curses.initscr()
  curses.echo()

  app = App(screen)

  c = screen.getstr()
  curses.endwin()

wrapper(main)

