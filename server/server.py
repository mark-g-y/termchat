import json
import logging
import Queue as queue
import random
import socket
import sys
import thread
import threading

HOST = '0.0.0.0'
PORT = 1738

random.seed(0)
client_queues_lock = threading.Lock()
client_queues = {}

logger = logging.getLogger('TermChat Logger')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('logs.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)

def receiver_thread(writer, chatroom_id, client_id):
  while True:
    try:
      logger.info('trying to read...' + str(client_id))
      message = client_queues[chatroom_id][client_id].get(block=True, timeout=10)
      logger.info('received message and now broadcasting: ' + message)
      writer.write(json.dumps({'type': 'message', 'text': message}) + '\n')
      writer.flush()
    except:
      # See if client is still alive.
      logger.info('seeing if client is alive' + str(client_id))
      try:
        writer.write(json.dumps({'type': 'ping'}) + '\n')
        writer.flush()
      except:
        logger.info('client disconnected' + str(client_id))
        break

def client_thread(reader, writer):
  global client_queues
  chatroom_id = None
  client_id = random.randint(0, 1000000)
  receiver_thread_id = None
  while True:
    data = reader.readline()
    if data.strip() == '':
      # Disconnected - leave
      client_queues_lock.acquire()
      if chatroom_id is not None and client_id is not None and client_queues.get(chatroom_id) is not None and client_queues[chatroom_id].get(client_id) is not None:
        del client_queues[chatroom_id][client_id]
      client_queues_lock.release()
      break
    data = json.loads(data)

    if data['type'] == 'subscribe':
      # Unsubscribe from current channel, if it exists
      client_queues_lock.acquire()

      if chatroom_id is not None and client_id is not None and client_queues.get(chatroom_id) is not None and client_queues[chatroom_id].get(client_id) is not None:
        del client_queues[chatroom_id][client_id]

      chatroom_id = data['chatroom_id']

      if client_queues.get(chatroom_id) is None:
        client_queues[chatroom_id] = {}
      client_queues[chatroom_id][client_id] = queue.Queue()

      receiver_thread_id = thread.start_new_thread(receiver_thread, (writer, chatroom_id, client_id, ))

      client_queues_lock.release()
    elif data['type'] == 'list_chatrooms':
      client_queues_lock.acquire()
      writer.write(json.dumps({'type': 'list_chatrooms', 'chatroom_ids': list(client_queues.keys())}) + '\n')
      writer.flush()
      client_queues_lock.release()
    elif data['type'] == 'message':
      client_queues_lock.acquire()
      if client_queues.get(chatroom_id) is not None:
        receivers = client_queues[chatroom_id]
        for receiver_id in receivers.keys():
            receivers[receiver_id].put(data['text'])
      else:
        logger.warning('Tried to write to non-existent chatroom ID - ' + str(chatroom_id))
      client_queues_lock.release()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

try:
  sock.bind((HOST, PORT))
except socket.error as msg:
  logger.error('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
  sys.exit()
  
sock.listen(10)

while True:
  conn, addr = sock.accept()
  logger.info('Connected with ' + addr[0] + ':' + str(addr[1]))

  reader  = conn.makefile('r')
  writer = conn.makefile('w')

  thread.start_new_thread(client_thread, (reader, writer, ))

sock.close()
