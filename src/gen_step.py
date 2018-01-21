
def gen():
    print('gen was call with None, runs all the way to first yield and stops after returning 1')
    v = 1
    rs = yield  v
    print('return value from previous send {} received from send: {}'.format(v, rs))
    v = 2
    rs = yield  v
    print('return value from previous send {} received from send: {}'.format(v, rs))


g = gen()
print('sending un to gen')
rc = g.send(None)
print('received from gen: {}'.format(rc))
print('sending deux to gen')
rc = g.send('deux')
print('received from gen: {}'.format(rc))
print('sending trois to gen')
try:
    rc = g.send('trois')
except StopIteration:
    print('The end')
print('received from gen: {}'.format(rc))
