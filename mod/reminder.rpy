default persistent._trm_queue = list()

init 10 python in trm_reminder:
    import store
    from store import persistent, mas_getEV, EV_ACT_QUEUE

    import datetime
    import time
    import math

    class Reminder(object):
        def __init__(
            self, trigger_at, target_evl,
            interval=None, grace_period=None, data=None,
            delegate_evl="trm_reminder_delegate", delegate_act=None
        ):
            if mas_getEV(target_evl) is None:
                raise ValueError("target event {0} does not exist".format(target_evl))
            if mas_getEV(delegate_evl) is None:
                raise ValueError("delegate event {0} does not exist".format(delegate_evl))

            if delegate_act is None:
                delegate_act = EV_ACT_QUEUE

            self.trigger_at = trigger_at
            self.target_evl = target_evl

            self.interval = interval
            self.grace_period = grace_period
            self.data = data
            self.delegate_evl = delegate_evl
            self.delegate_act = delegate_act


        def __eq__(self, other):
            return (
                self.trigger_at == other.trigger_at and
                self.target_evl == other.target_evl and
                self.interval == other.interval and
                self.grace_period == other.grace_period and
                self.data == other.data and
                self.delegate_evl == other.delegate_evl and
                self.delegate_act == other.delegate_act
            )


        @property
        def due(self):
            if self.grace_period is None:
                return self.trigger_at <= datetime.datetime.now()
            return self.trigger_at <= datetime.datetime.now() < self.trigger_at + self.grace_period


    # Export Reminder with prefix to global store.
    store.trm_Reminder = Reminder


    def queue_reminder(reminder):
        """
        Appends reminder to the queue and sorts it.

        IN:
            reminder -> Reminder:
                Reminder object to add to queue.
        """

        persistent._trm_queue.append(reminder)
        __sort_queue()


    def pop_reminder():
        """
        Pops the next reminder (or extends it and updates the queue) and returns
        it. Raises an error in case queue is empty or if a reminder is before due.

        OUT:
            Reminder:
                Next reminder that is due or overdue. Reminder#due() can be used
                to check if reminder is exactly due and not past grace period.

        RAISES:
            ValueError:
                When queue is empty or when next reminder is before due.
        """

        if len(persistent._trm_queue) == 0:
            raise ValueError("queue is empty")

        reminder = persistent._trm_queue[0]
        now = datetime.datetime.now()

        if reminder.trigger_at > now:
            raise ValueError("cannot pop reminder that is before due")

        if reminder.interval is not None:
            # Since this reminder has an interval and is extensible, don't drop
            # it from this queue but reuse and sort queue again.
            # Arming/disarming delegates is done in queue sort routine.
            __extend_reminder(reminder)
            __sort_queue()

        else:
            # The queue is sorted here, no need to sort again; just drop reminder
            # from this queue and disarm it, then arm next one if any.
            persistent._trm_queue.pop(0)
            __disarm_reminder_delegate(reminder)
            if len(persistent._trm_queue) > 0:
                __arm_reminder_delegate(persistent._trm_queue[0])

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

        if len(persistent._trm_queue) > 1:
            curr_rem = persistent._trm_queue[0]
            persistent._trm_queue.sort(key=lambda reminder: reminder.trigger_at)
            if persistent._trm_queue[0] != curr_rem:
                # Next reminder isn't the one we had before, reset its delegate.
                __disarm_reminder_delegate(curr_rem)

        if len(persistent._trm_queue) > 0:
            # And setup a new delegate.
            __arm_reminder_delegate(persistent._trm_queue[0])


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