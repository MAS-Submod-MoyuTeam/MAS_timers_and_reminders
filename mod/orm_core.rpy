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


    class DNDict(dict):
        def __init__(self, *args, **kw):
            super(DNDict, self).__init__(*args, **kw)

        def __getattr__(self, attr):
            try:
                return getattr(super(DNDict, self), attr)
            except AttributeError:
                return self[attr]


    class Target(object):
        def __init__(
            self,
            key, event_label, trigger_at,
            grace_period=datetime.timedelta(seconds=3600), data=None,
            delegate_evl="otter_reminder_delegate", delegate_act=EV_ACT_QUEUE
        ):
            if not store.mas_getEV(event_label):
                raise ValueError("event {0} does not exist".format(event_label))
            if not store.mas_getEV(delegate_evl):
                raise ValueError("delegate event {0} does not exist".format(delegate_evl))

            self.key = key
            self.event_label = event_label
            self.trigger_at = trigger_at
            self.grace_period = grace_period
            if type(data) is dict:
                self.data = DNDict(data)

            self.delegate_evl = delegate_evl
            self.delegate_act = delegate_act

        @property
        def overdue(self):
            return self.trigger_at + self.grace_period < datetime.datetime.now()

    # Reminder is a non-extensible, one-shot target that fires once and
    # completes. Not to be confused with Timer which is repeatable.
    class Reminder(Target):
        def __init__(self, key, event_label, trigger_at, grace_period, interval, data=None):
            super(Reminder, self).__init__(key, event_label, trigger_at, grace_period, data)
            self.interval = interval

    # Timer is an extensible, repeatable target that fires multiple times
    # with set interval.
    class Timer(Target):
        def __init__(self, key, event_label, trigger_at, grace_period, data=None):
            super(Timer, self).__init__(key, event_label, trigger_at, grace_period, data)

    store.orm_Reminder = Reminder
    store.orm_Timer = Timer


    def add_target(target):
        persistent._orm_target_queue.append(target)
        if type(orm_target) is orm_Timer:
            extend_target()
        elif type(orm_target) is orm_Reminder:
            orm_cleanupTarget()
        setup_target()


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

        This function MUST be called in delegate event, but ONLY after
        orm_extendTarget or orm_cleanupTarget calls.
        """

        while True:
            if not persistent._orm_target_queue:
                return

            persistent._orm_target_queue.sort(key=lambda e: e[1].trigger_at)
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

        ev.start_date = None
        ev.end_date = None
        ev.action = None

        persistent._orm_target_queue.pop(0)

    store.orm_addTarget = add_target
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
    python:
        if type(orm_target) is orm_Timer:
            orm_extendTarget()
        elif type(orm_target) is orm_Reminder:
            orm_cleanupTarget()
        pushEvent(orm_target.event_label)
        setup_target()
    return