import time
import json
import redis
import threading
import board
import neopixel


# list to maintain pod state
pending_pods = []
running_pods = []
terminating_pods = []
led_arr = []

# NeoPixel Stick connected to GPIO Pin 8
GPIO_PIN = 8

pixels = neopixel.NeoPixel(board.D18, GPIO_PIN, brightness=0.2)
pixels.fill((0, 0, 0))

# Connect to Redis
r = redis.Redis(host='localhost', port=6379)
key = 'status'
p = r.pubsub(ignore_subscribe_messages=True)

p.subscribe(key)


# Flash Red when pod is terminated
def flash_red(index_to_blink):
    pixels[index_to_blink] = (0, 0, 0)
    time.sleep(0.2)
    pixels[index_to_blink] = (255, 0, 0)
    time.sleep(0.2)
    pixels[index_to_blink] = (0, 0, 0)


# Map colors to RGB values for neopixel stick
def map_func(color):
    color = color.decode('utf-8')
    if color == 'red':
        return (255, 0, 0)
    elif color == 'green':
        return (0, 255, 0)
    elif color == 'blue':
        return (0, 0, 255)


def check_stat(data):
        typ = data['type']
        phase = data['phase']
        podname = data['pod']

        if typ == 'ADDED' and phase == 'Pending':
            pending_pods.append(podname)
            r.rpush(key, 'green')
            # print('Container Creating:', podname)

        elif typ == 'ADDED' and phase == 'Running':
            running_pods.append(podname)
            r.lpush(key, 'blue')
            # print('Running:', podname)

        elif typ == 'MODIFIED' and phase == 'Running':
            if podname in pending_pods:
                pending_pods.remove(podname)
                r.lrem(key, 1, 'green')
                running_pods.append(podname)
                r.lpush(key, 'blue')
                # print('Running:', podname)

            elif podname in running_pods:
                running_pods.remove(podname)
                r.lrem(key, 1, 'blue')
                terminating_pods.append(podname)
                r.rpush(key, 'red')
                # print('Terminating:', podname)

        elif typ == 'DELETED' and (phase == 'Pending' or phase == 'Running'):
            if podname in terminating_pods:
                terminating_pods.remove(podname)
                r.lrem(key, 1, 'red')
                ## flash red in another thread

                # get length of the list representing the led array
                index_to_blink = r.llen(key)
                t1 = threading.Thread(target=flash_red, args=(index_to_blink,))
                t1.start()
                index_to_blink = 0

                # print('Terminated:', podname)
            elif podname in pending_pods:
                pending_pods.remove(podname)
                r.lrem(key, 1, 'green')
                ## flash red in another thread

                # get length of the list representing the led array
                index_to_blink = r.llen(key)
                t2 = threading.Thread(target=flash_red, args=(index_to_blink,))
                t2.start()
                index_to_blink = 0

#  Watch over the subscribed topic
for message in p.listen():
    message = json.loads(message['data'])
    pixels.fill((0, 0, 0))
    check_stat(message)
    print(r.lrange(key, 0, 7))

    # get the RGB representation of states for the stick
    led_arr = list(map(map_func, r.lrange(key, 0, 7)))
    # add padding to iterate over for empty slots in stick
    padding = [(0, 0, 0)] * (8 - len(led_arr))
    led_arr = led_arr + padding
    
    for i in range(0, 8):
        pixels[i] = led_arr[i]
        pixels.show()
    print(led_arr)