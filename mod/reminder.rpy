define persistent._trm_queue = list()


init 10 python in trm_reminder:

    import store
    from store import persistent, mas_getEV, EV_ACT_QUEUE

    import datetime
    import time
    import math
    import collections


    class Reminder(object):
        def __init__(
            self, trigger_at, target_evl, key, prompt,
            interval=None, grace_period=None, data=None,
            delegate_evl="trm_reminder_delegate", delegate_act=None
        ):
            if mas_getEV(target_evl) is None:
                raise ValueError("target event {0} does not exist".format(target_evl))
            if mas_getEV(delegate_evl) is None:
                raise ValueError("delegate event {0} does not exist".format(delegate_evl))

            if delegate_act is None:
                delegate_act = EV_ACT_QUEUE

            self.key = key
            self.prompt = prompt
            self.trigger_at = trigger_at
            self.target_evl = target_evl

            self.interval = interval
            self.grace_period = grace_period
            self.data = data
            self.delegate_evl = delegate_evl
            self.delegate_act = delegate_act


        def __eq__(self, other):
            return isinstance(self, type(other)) and self.key == other.key


        def __hash__(self):
            return hash(self.key)


        def to_dict(self):
            return dict(
                trigger_at=self.trigger_at,
                target_evl=self.target_evl,
                key=self.key,
                prompt=self.prompt,
                interval=self.interval,
                grace_period=self.grace_period,
                data=self.data,
                delegate_evl=self.delegate_evl,
                delegate_act=self.delegate_act
            )


        @property
        def due(self):
            if self.grace_period is None:
                return self.trigger_at <= datetime.datetime.now()
            return self.trigger_at <= datetime.datetime.now() < self.trigger_at + self.grace_period

    # Export Reminder with prefix to global store.
    store.trm_Reminder = Reminder

    # Create queue that holds actual Reminder objects which will be persisted
    # as dictionaries because otherwise after uninstall users will end up with
    # corrupted persistent.
    queue = list()


    def get_reminders():
        """
        Returns all queued reminders as ordered dictionary (preserving their
        queue positions) of reminder keys as keys and reminders as values.

        OUT:
            collections.OrderedDict:
                Reminders in queue.
        """

        view = collections.OrderedDict()
        for rem in queue:
            view[rem.key] = rem
        return view


    def queue_reminder(reminder):
        """
        Appends reminder to the queue and sorts it.

        IN:
            reminder -> Reminder:
                Reminder object to add to queue.
        """

        queue.append(reminder)
        __sort_queue()
        __persist_queue()


    def dequeue_reminder(query):
        """
        Removes reminder located by the specified query parameter from the
        queue and returns it.

        IN:
            query -> str or Reminder:
                Value to lookup Reminder by, if str then key lookup is
                performed, if Reminder then hash lookup is performed.

        OUT:
            Reminder:
                Reminder that was dequeued if lookup was successful.
            None:
                None if lookup failed.
        """

        search_list = queue

        if isinstance(query, str):
            search_list = list(map(lambda it: it.key, queue))

        try:
            return pop_reminder(search_list.index(query), remove=True)
        except ValueError as e:
            return None


    def pop_reminder(index=None, remove=False):
        """
        Pops the next (or specified) reminder (or extends it and updates the
        queue) and returns it. Raises an error in case queue is empty or if a
        reminder is before due.

        IN:
            index -> int or None, default None:
                Index of reminder to remove or None to remove next.

            remove -> bool, default False:
                If True, remove a reminder, don't extend.

        OUT:
            Reminder:
                Next (or specified) reminder that is due or overdue.
                Reminder#due() can be used to check if reminder is exactly due
                and not past grace period.

        RAISES:
            ValueError:
                When queue is empty or when next (or specified) reminder is
                before due.
        """

        if index is None:
            index = 0

        if len(queue) == 0:
            raise ValueError("queue is empty")

        reminder = queue[index]
        if reminder.interval is not None and not remove:
            # Since this reminder has an interval and is extensible, don't drop
            # it from this queue but reuse and sort queue again.
            # Arming/disarming delegates is done in queue sort routine.
            __extend_reminder(reminder)
            __sort_queue()

        else:
            # The queue is sorted here, no need to sort again; just drop reminder
            # from this queue and disarm it, then arm next one if any.
            queue.pop(index)
            __disarm_reminder_delegate(reminder)
            if len(queue) > 0:
                __arm_reminder_delegate(queue[0])

        # Commit changes in queue to persistent.
        __persist_queue()

        return reminder


    def __extend_reminder(reminder):
        """
        Extends the provided reminder (but does not modify queue or arm
        delegate event) so that its new trigger timestamp is bumped up to
        the next closest trigger time using reminder interval as bump step.

        Also, a no-op when reminder is before due.

        IN:
            reminder -> Reminder:
                Reminder object to extend, must have interval set.

        RAISES:
            ValueError:
                If reminder has no interval.
        """

        if reminder.interval is None:
            raise ValueError("reminder has no interval")

        now_ts = int(time.time())
        trigger_ts = __dt_timestamp(reminder.trigger_at)

        if trigger_ts > now_ts:
            return

        diff = now_ts - trigger_ts
        iters = math.ceil(diff / reminder.interval)
        reminder.trigger_at += reminder.interval * iters


    def __sort_queue():
        """
        Sorts reminders queue (no-op when queue has 0-1 items) and additionally
        arms/disarms reminder delegates.
        """

        if len(queue) > 1:
            curr_rem = queue[0]
            queue.sort(key=lambda reminder: reminder.trigger_at)
            if queue[0] != curr_rem:
                # Next reminder isn't the one we had before, reset its delegate.
                __disarm_reminder_delegate(curr_rem)

        if len(queue) > 0:
            # And setup a new delegate.
            __arm_reminder_delegate(queue[0])


    def __load_queue():
        global queue
        queue = list()
        for rem_dict in persistent._trm_queue:
            queue.append(Reminder(**rem_dict))


    def __persist_queue():
        persistent._trm_queue = list()
        for rem in queue:
            persistent._trm_queue.append(rem.to_dict())


    def __arm_reminder_delegate(reminder):
        """
        Arms reminder delegate event; namely, sets the following attributes of
        the delegate event:

            * start date (reminder trigger timestamp)
            * end date (trigger timestamp + trigger grace period if any)
            * action (reminder delegate action)

        Custom delegate event authors must keep that in mind.

        IN:
            reminder -> Reminder:
                Reminder object to arm delegate event for.
        """

        ev = mas_getEV(reminder.delegate_evl)
        ev.start_date = reminder.trigger_at
        if reminder.grace_period is not None:
            ev.end_date = reminder.trigger_at + reminder.grace_period
        ev.action = reminder.delegate_act


    def __disarm_reminder_delegate(reminder):
        """
        Disarms reminder delegate event; namely, resets to None the following
        attributes of the delegate event:

            * start date
            * end date
            * action

        Custom delegate event authors must keep that in mind.

        IN:
            reminder -> Reminder:
                Reminder object to disarm delegate event for.
        """

        ev = mas_getEV(reminder.delegate_evl)
        ev.start_date = None
        ev.end_date = None
        ev.action = None


    def __dt_timestamp(dt):
        """
        Retrieves Unix timestamp (seconds since 1970) from the provided datetime
        object (a workaround solution since Python 2 has no timestamp() function.)

        IN:
            dt -> datetime.datetime:
                DateTime object to get timestamp from.

        OUT:
            int:
                Timestamp of the provided DateTime object.
        """

        return int(time.mktime(dt.utctimetuple()) * 1000 + dt.microsecond / 1000)


    # Load queue from persistent on start.
    __load_queue()


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="trm_reminder_delegate"
        ),
        code="EVE"
    )

label trm_reminder_delegate:
    $ reminder = store.trm_reminder.pop_reminder()
    if reminder.due:
        # If this reminder is past trigger time but within grace period
        # or doesn't have one, queue it. Else silently drop.
        $ MASEventList.queue(reminder.target_evl)

    # Queueing the target event will make it fire immediately after this event
    # returns to the loop, effectively meaning no visible delay for user.
    return