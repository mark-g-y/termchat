import json
import queue
import random
import socket
import sys
import thread
import threading

HOST = 'localhost'
PORT = 1738

random.seed(0)
client_queues_lock = threading.Lock()
client_queues = {}

def receiver_thread(conn, chatroom_id, client_id):
  while True:
    message = client_queues[chatroom_id][client_id].get(block=True)
    conn.send(json.dumps({'type': 'message', 'text': message}))

def client_thread(conn):
  global client_queues
  chatroom_id = None
  client_id = random.randint(0, 1000000)
  receiver_thread_id = None
  while True:
    data = conn.recv(2048)
    print data
    print 'space'
    data = json.loads(data)

    if data['type'] == 'subscribe':
      # Unsubscribe from current channel, if it exists
      client_queues_lock.acquire()

      if chatroom_id is not None and client_id is not None and client_queues.get(chatroom_id) is not None and client_queues[chatroom_id].get(client_id) is not None:
        del client_queues[chatroom_id][client_id]

      chatroom_id = data['chatroom_id']

      client_queues[chatroom_id] = {}
      client_queues[chatroom_id][client_id] = queue.Queue()

      # TODO: stop old thread
      receiver_thread_id = thread.start_new_thread(receiver_thread, (conn, chatroom_id, client_id, ))

      client_queues_lock.release()
    elif data['type'] == 'list_chatrooms':
      client_queues_lock.acquire()
      conn.send(json.dumps({'type': 'list_chatrooms', 'chatroom_ids': list(client_queues.keys())}))
      client_queues_lock.release()
    elif data['type'] == 'message':
      client_queues_lock.acquire()
      receivers = client_queues[chatroom_id]
      for receiver_id in receivers.keys():
        receivers[receiver_id].put(data['text'])
      client_queues_lock.release()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

try:
  sock.bind((HOST, PORT))
except socket.error as msg:
  print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
  sys.exit()
  
sock.listen(10)

while True:
  conn, addr = sock.accept()
  print 'Connected with ' + addr[0] + ':' + str(addr[1])

  thread.start_new_thread(client_thread, (conn, ))

sock.close()