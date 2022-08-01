## custom reminder goes here! let me know whenever you need dialogue or expressions! or any help at all!!!!

# Target queue: this variable holds queue of upcoming targets (timers,
# reminders, etc.)
# First element (if queue is not empty) is current target.
default persistent._orm_target_queue = list()

init 10 python in otter_reminder:
    _LOG_PREFIX = "[MAS Reminders Mod] "

    def log_info(msg):
        store.mas_submod_utils.submod_log.info(_LOG_PREFIX + msg)

    def log_warning(msg):
        store.mas_submod_utils.submod_log.warning(_LOG_PREFIX + msg)

    def log_error(msg):
        store.mas_submod_utils.submod_log.error(_LOG_PREFIX + msg)


    class Target(object):
        def __init__(
            self,
            key, event_label, trigger_at, grace_period, data=None,
            delegate_evl="otter_reminder_delegate", delegate_act=EV_ACT_QUEUE
        ):
            if not store.mas_getEV(delegate_evl):
                raise ValueError("delegate event {0} does not exist".format(delegate_evl))

            self.key = key
            self.event_label = event_label
            self.trigger_at = trigger_at
            self.grace_period = grace_period
            self.data = data

            self.delegate_evl = delegate_evl
            self.delegate_act = delegate_act

        @property
        def overdue(self):
            return self.trigger_at + self.grace_period < datetime.datetime.now()

        def __lt__(self, other):
            return self.trigger_at < other.trigger_at

        def __le__(self, other):
            return self.trigger_at <= other.trigger_at

        def __gt__(self, other):
            return self.trigger_at > other.trigger_at

        def __ge__(self, other):
            return self.trigger_at >= other.trigger_at

        def __eq__(self, other):
            return self.trigger_at == other.trigger_at

        def __ne__(self, other):
            return self.trigger_at != other.trigger_at

    class Reminder(Target):
        def __init__(self, key, event_label, trigger_at, grace_period, interval, data=None):
            super(TimeTriggerable, self).__init__(key, event_label, trigger_at, grace_period, data)
            self.interval = interval

    class Timer(Target):
        def __init__(self, key, event_label, trigger_at, grace_period, data=None):
            super(TimeTriggerable, self).__init__(key, event_label, trigger_at, grace_period, data)

    store.ORM_TARGET_REMINDER = Reminder
    store.ORM_TARGET_TIMER = Timer


    def setup_target():
        """
        Sets up next target to trigger. Additionally, performs a safety check
        that delegate event actually exists or if queue is empty. Both of the
        abovementioned cases are no-op and only create log entries.

        Performs a mutating sort on target queue in order to move the closest
        (or overdue) target to the head of the queue; to this function there
        is no difference between upcoming and overdue targets.

        In delegate events (and subsequent frames created by 'call') globally
        exported variable 'orm_target' is available. This variable of Target
        type holds useful properties 'overdue' and 'data' that can be used
        in script logic.
        """

        while True:
            if not persistent._orm_target_queue:
                log_info("Target queue is empty, nothing to set up. Waiting for next setup_target call.")
                return

            persistent._orm_target_queue.sort(key=lambda e: e[1])
            target = persistent._orm_target_queue[0]

            ev = store.mas_getEV(target.delegate_evl)
            if not ev:
                log_error("Delegate event {0} for target {1} does not exist, discarding target from the queue.".format(target.delegate_evl, target.key))
                persistent._orm_target_queue.pop(0)
                return

            break

        store.orm_target = target

        ev.start_date = target.trigger_at
        ev.end_date = target.trigger_at + target.grace_period
        ev.action = target.delegate_act

    def extend_target():
        """
        Extends target trigger date and updates delegate event (internally calls
        setup_target function after all the checks and manipulations.)

        This function MUST be called in delegate event, but ONLY if this is
        Reminder type of target.
        """

        if not persistent._orm_target_queue:
            log_info("Target queue is empty, nothing to extend. Waiting for next setup_target call.")
            return

        target = persistent._orm_target_queue[0]
        if type(target) is not Timer:
            log_error("Attempted to extend target {0} which is not of type Timer.".format(target.key))
            return

        ev = store.mas_getEV(target.delegate_evl)
        if not ev:
            log_error("Delegate event {0} for target {1} does not exist, unable to extend timer.".format(target.delegate_evl, target.key))
            return

        target.trigger_at += target.interval
        setup_target()

    def cleanup_target():
        """
        Cleans up delegate event (strips it off start/end date and action) and
        removes persistent and stored variables related to current target and
        removes it from the queue. If there is no current target, this function
        does nothing.

        This function MUST be called in delegate event, but ONLY if this is not
        Timer type of target.
        """

        if not persistent._orm_target_queue:
            return

        ev = store.mas_getEV(persistent._orm_target_queue[0].delegate_evl)
        if not ev:
            log_error("Delegate event {0} for target {1} does not exist, unable to perform cleanup.".format(target.delegate_evl, target.key))
            return

        persistent._orm_target_queue.pop(0)
        del store.orm_target

        ev.start_date = None
        ev.end_date = None
        ev.action = None

    store.orm_extendTarget = extend_target
    store.orm_cleanupTarget = cleanup_target

init 5 python:
    addEvent(
        Event(
            persitent.event_database,
            eventlabel="otter_reminder_delegate"
        ),
        code="EVE"
    )

label otter_reminder_delegate:
    call expression orm_target.event_label
    python:
        if type(orm_target) is ORM_TARGET_TIMER:
            orm_extendTarget()
        elif type(orm_target) is ORM_TARGET_REMINDER:
            orm_cleanupTarget()
    return _return