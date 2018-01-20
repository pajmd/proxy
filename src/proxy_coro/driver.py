from promise import Promise

class Driver(object):

    def __init__(self, coro):
        self.coro = coro
        p = Promise()
        p.set_result(None)
        self.step(p)

    def step(self, promise):
        try:
            next_promise = self.coro.send(promise.result)
        except StopIteration:
            return

        next_promise.add_done_callback(self.step)