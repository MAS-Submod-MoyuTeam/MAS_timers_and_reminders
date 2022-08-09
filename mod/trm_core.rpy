## Queue that stores timers.
default persistent._trm_queue = list()

init python in trm_core:
    import store

## Logging functions and constants

    from store.mas_logging import submod_log


    LOG_PREFIX = "[Timers and Reminders] "


    def info(msg):
        submod_log.info(LOG_PREFIX + msg)


    def info(msg):
        submod_log.info(LOG_PREFIX + msg)


    def info(msg):
        submod_log.info(LOG_PREFIX + msg)


## Timer object

    from store import persistent
    from store import EV_ACT_QUEUE


    class Timer(object):
        def __init__(
            self, key, trigger,
            eventlabel, action=EV_ACT_QUEUE,
            grace=None, interval=None, data=None
        ):
            """
            IN:
                key - unique key to identify this very timer with.
                trigger - datetime to trigger this timer at
                eventlabel - label of an event to perform action on
                action - action to set event action to
                grace - timedelta period between trigger time and expire time
                interval - timedelta interval to add to trigger time after timer
                    triggers (to create a recurring timer)
                data - any arbitrary data to expose to event
            """
            self.key = key
            self.trigger = trigger

            self.eventlabel = eventlabel
            self.action = action

            self.grace = grace
            self.interval = interval
            self.data = data

        @property
        def now(self):
            """
            OUT:
                True if self.grace is not None and current system time is
                between self.trigger and self.trigger + self.grace.
                Always False if self.grace is None; use self.overdue to check
                in this case.
            """

            if self.grace:
                return self.trigger <= datetime.datetime.now() < self.trigger + self.grace
            return False

        @property
        def overdue(self):
            """
            OUT:
                If self.grace is not None: True if current system time is
                after self.trigger + self.grace; else True if self.trigger is
                before current system time.
            """

            if self.grace:
                return self.trigger + self.grace < datetime.datetime.now()
            return self.trigger < datetime.datetime.now()

        @property
        def recurring(self):
            """
            OUT:
                True if self.interval is not None.
            """

            return self.interval is not None


## Queue control functions

    queue = persistent._trm_queue


    def queue(timer):
        # Append timer to queue and re-sort the queue.
        queue.append(timer)
        __sort_reset_queue(queue)


    def dequeue_or_extend():
        if queue[0].recurring:
            extend_current()
        else:
            dequeue_current()


    def extend_current():
        # Wind up its trigger time again and re-sort the queue. No need to reset
        # the event here, this will be handled in __sort_reset_queue.
        now = datetime.datetime.now()
        while timer.trigger >= now:
            timer.trigger += timer.interval
        __sort_reset_queue(queue)


    def dequeue_current():
        # Reset this timer and and pop from queue. No need to re-sort the queue,
        # it will already be in proper order by now.
        __reset_timer_event(timer)
        queue.pop(0)


    def dequeue(key):
        # Remove timer by key and update persistent variable.
        queue = filter(lambda e: e.key != key, queue)
        persistent._trm_queue = queue


## Event operation functions

    from store import mas_getEV


    def __sort_reset_queue():
        # If queue is empty, we can just setup new timer and that's it.
        if not queue:
            __setup_timer_event(timer)

        # If not, we need to keep the reference to the old next event (first
        # event in the queue), sort the queue, reset old next event and setup
        # new next event.
        else:
            old_next_t = queue[0]
            queue.sort(key=lambda e: e.trigger)
            if old_next_t != queue[0]:
                __reset_timer_event(old_next_t)
            __setup_timer_event(queue[0])


    def __setup_timer_event(timer):
        ev = mas_getEV(timer.eventlabel)
        ev.start_date = timer.trigger
        if timer.grace:
            ev.end_date = timer.trigger + timer.grace
        ev.action = timer.action


    def __reset_timer_event(timer):
        ev = mas_getEV(timer.eventlabel)
        ev.start_date = None
        ev.end_date = None
        ev.action = None