# Dev/test file for timers/reminders. Remove when we've got proper topic for it.

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="trm_dev_timer_new",
            prompt="Can you set up a new timer for me?",
            category=["timers and reminders"],
            unlocked=True,
        ),
        code="EVE"
    )

label trm_dev_timer_new:
    m "Sure!"
    m "Let me write a note for myself... What do you want me to remind you about?"

    python:
        note = mas_input(
            "What to remind about?",
            allow="abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ-_0123456789",
            length=32,
            screen_kwargs={"use_return_button": False}
        )

    m "Okay... Now when do you want me to remind you about it?{nw}"
    $ _history_list.pop()
    menu:
        m "Okay... Now when do you want me to remind you about it?{fast}"

        "In an hour.":
            $ delay = datetime.timedelta(seconds=3600)

        "In two hours.":
            $ delay = datetime.timedelta(seconds=3600*2)

        "In three hours.":
            $ delay = datetime.timedelta(seconds=3600*3)

        "In six hours.":
            $ delay = datetime.timedelta(seconds=3600*6)

        "In twelve hours.":
            $ delay = datetime.timedelta(seconds=3600*12)

        "In a day.":
            $ delay = datetime.timedelta(days=1)

    python:
        store.trm_core.queue_timer(store.trm_core.Timer(
            key=note,
            trigger=datetime.datetime.now() + delay,
            eventlabel="trm_dev_timer_event",
            grace=datetime.timedelta(seconds=3600)
        ))

    m "Okay! I'll be sure not to forget~"

    return


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="trm_dev_timer_repeatable_new",
            prompt="Can you set up a new repeatable timer for me?",
            category=["timers and reminders"],
            unlocked=True,
        ),
        code="EVE"
    )

label trm_dev_timer_repeatable_new:
    m "Sure!"
    m "Let me write a note for myself... What do you want me to remind you about?"

    python:
        note = mas_input(
            "What to remind about?",
            allow="abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ-_0123456789",
            length=32,
            screen_kwargs={"use_return_button": False}
        )

    m "Okay... Now when do you want me to remind you about it?{nw}"
    $ _history_list.pop()
    menu:
        m "Okay... Now when do you want me to remind you about it?{fast}"

        "In an hour.":
            $ delay = datetime.timedelta(seconds=3600)

        "In two hours.":
            $ delay = datetime.timedelta(seconds=3600*2)

        "In three hours.":
            $ delay = datetime.timedelta(seconds=3600*3)

        "In six hours.":
            $ delay = datetime.timedelta(seconds=3600*6)

        "In twelve hours.":
            $ delay = datetime.timedelta(seconds=3600*12)

        "In a day.":
            $ delay = datetime.timedelta(days=1)

    python:
        store.trm_core.queue_timer(store.trm_core.Timer(
            key=note,
            trigger=datetime.datetime.now() + delay,
            interval=datetime.timedelta(seconds=10),
            eventlabel="trm_dev_timer_event",
            grace=datetime.timedelta(seconds=3600)
        ))

    m "Okay! I'll be sure not to forget~"

    return


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="trm_dev_timer_event"
        ),
        code="EVE"
    )

label trm_dev_timer_event:
    m "[player], you told me to remind you about something!"
    m "Let me read..."
    $ note = store.trm_core.timer.key
    m "'[note]!'"
    m "Hope it helped~"
    $ store.trm_core.dequeue_or_extend()
    return