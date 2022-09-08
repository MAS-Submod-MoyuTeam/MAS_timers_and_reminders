init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="dev_trm_test",
            prompt="TEST REMINDER",
            category=["DEV"],
            pool=True,
            unlocked=True
        ),
        code="EVE"
    )

label dev_trm_test:
    m 1eua "Okay [player], now I'll create a reminder with random number..."
    m 3eub "It'll appear as another event shortly!"
    python:
        store.trm_reminder.queue_reminder(trm_Reminder(
            trigger_at=datetime.datetime.now() + datetime.timedelta(seconds=10),
            target_evl="dev_trm_reminder",
            data=renpy.random.randint(0, 100)
        ))
    return


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="dev_trm_reminder"
        ),
        code="EVE"
    )

label dev_trm_reminder:
    $ data = reminder.data
    m 1hua "Got a reminder for you! Data is... [data]!"
    return

