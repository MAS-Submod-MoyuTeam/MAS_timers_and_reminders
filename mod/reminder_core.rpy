define persistent._trm_queue = list()


init 10 python in _trm_reminder:

    import store
    from store import persistent, mas_getEV, EV_ACT_QUEUE

    import datetime
    import time
    import math
    import collections


    class Reminder(object):
        """
        Reminder represents a Reminder, recurring or one-shot. Recurring
        reminders have interval set, one-shot reminders have not.

        Reminders integrate with queue that updates their delegate events with
        trigger datetimes and actions and, correspondingly, delegate events that
        keep the queue going.
        """

        def __init__(
            self, trigger_at, target_evl, key, prompt,
            interval=None, grace_period=None, data=None,
            delegate_evl="trm_reminder_delegate", delegate_act=None
        ):
            """
            Create an instance of Reminder with the provided properties.

            IN:
                trigger_at -> datetime.datetime:
                    Date and time to trigger this reminder at.
                    NOTE: due to how MAS events work, there is no guarantee it
                    will trigger right at this date and time. It will always be
                    delayed by some insignificant amount of time.

                target_evl -> str:
                    Target event label to queue for this reminder.

                key -> str:
                    Unique key used to distinguish two reminders from each
                    other.

                prompt -> str:
                    Prompt of this Reminder, user's note attached to it.

                interval -> datetime.timedelta or None, default None:
                    Interval to set for this recurring Reminder. If None, then
                    this Reminder is one-shot.

                grace_period -> datetime.timedelta or None, default None:
                    Grace period to set for this reminder. If None, then this
                    Reminder has no grace period and it will always be due and
                    never overdue.

                data -> any or None, default None:
                    Arbitrary data to assign to this Reminder to use in
                    triggered topics and reminder handlers.

                delegate_evl -> str or None, default "trm_reminder_delegate":
                    Event label of delegate event that will be queued for this
                    Reminder after it has been processed by the queue.

                delegate_act -> str or None, default EV_ACT_QUEUE:
                    Action to use on delegate event.
            """

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

        @property
        def due(self):
            """
            Checks if this Reminder is due its date and time:

                * If grace period is set, it checks if this Reminder is past
                  its trigger date and time and before the grace period ends.
                * If grace period is not set, it checks if this Reminder is
                  past its trigger date.

            OUT:
                bool:
                    True if this reminder is due its date and time.
            """

            now = datetime.datetime.now()

            # NOTE: This is a crude workaround, need a better way to handle
            #  extension in recurring reminders as this check is made AFTER
            #  recurring rendering it unqueued otherwise.
            if self.trigger_at > now and self.interval is not None:
                now += self.interval

            if self.grace_period is None:
                return self.trigger_at <= now
            return self.trigger_at <= now < self.trigger_at + self.grace_period

        @property
        def remaining(self):
            """
            Returns timedelta between current date and time and trigger date and
            time.

            OUT:
                datetime.timedelta:
                    Time until this Reminder triggers.
            """

            return self.trigger_at - datetime.datetime.now()

        @staticmethod
        def from_dict(_dict):
            """
            Deserializes dictionary object produced by to_dict method to an
            object instance of this Reminder class.

            IN:
                _dict -> dict[str, any]:
                    Serialized dictionary to deserialize.

            OUT:
                Reminder:
                    Reminder deserialized from provided dictionary.
            """

            return Reminder(**_dict)

        def to_dict(self):
            """
            Serializes this Reminder object to dictionary for storing it in
            persistent where it is problematic to keep actual class objects in.

            OUT:
                dict:
                    Dictionary compatiblee with from_dict static method.
            """

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

        def __eq__(self, other):
            """
            Compares this Reminder object to any other object and returns bool
            value if they are equal or not.

            IN:
                other -> any:
                    Object to compare with.

            OUT:
                bool:
                    True if objects are equal, False otherwise.
            """

            return isinstance(self, type(other)) and self.key == other.key

        def __hash__(self):
            """
            Generates a hash for this Reminder object based on its key.

            OUT:
                int:
                    Hash for this Reminder object.
            """

            return hash(self.key)


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

        # NOTE: *IDEALLY* this has to be done math way without any loops
        #  so no CPU cycles wasted on such a simple task.

        # now_ts = __dt_timestamp(datetime.datetime.now())
        # trigger_ts = __dt_timestamp(reminder.trigger_at)

        now = datetime.datetime.now()

        # if trigger_ts > now_ts:
        if reminder.trigger_at > now:
            return

        while reminder.trigger_at < now:
            reminder.trigger_at += reminder.interval

        # diff = now_ts - trigger_ts
        # iters = math.ceil(diff / int(reminder.interval.total_seconds()))
        # reminder.trigger_at += reminder.interval * iters


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
        """
        Load and deserialize (from dictionary objects) queue from persistent.
        """

        global queue
        queue = list()
        for rem_dict in persistent._trm_queue:
            queue.append(Reminder.from_dict(rem_dict))


    def __persist_queue():
        """
        Serialize (to dictionary objects) and write reminders queue to
        persistent.
        """

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
    $ reminder = store._trm_reminder.pop_reminder()
    if reminder.due:
        # If this reminder is past trigger time but within grace period
        # or doesn't have one, queue it. Else silently drop.
        $ MASEventList.queue(reminder.target_evl)

    # Queueing the target event will make it fire immediately after this event
    # returns to the loop, effectively meaning no visible delay for user.
    return