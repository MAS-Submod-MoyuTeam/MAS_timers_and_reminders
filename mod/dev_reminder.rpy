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
        n = renpy.random.randint(0, 100)
        store.trm_reminder.queue_reminder(trm_Reminder(
            key="random_" + str(n),
            prompt="Reminder n=" + str(n),
            trigger_at=datetime.datetime.now() + datetime.timedelta(seconds=10),
            target_evl="dev_trm_reminder",
            data=dict(n=n)
        ))
    return


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="dev_trm_test_recurring",
            prompt="TEST REMINDER RECURRING",
            category=["DEV"],
            pool=True,
            unlocked=True
        ),
        code="EVE"
    )

label dev_trm_test_recurring:
    m 1eua "Okay [player], now I'll create a reminder with random number..."
    m 3eub "It'll appear as another event shortly and will repeat!"
    python:
        n = renpy.random.randint(0, 100)
        store.trm_reminder.queue_reminder(trm_Reminder(
            key="random_" + str(n),
            prompt="Reminder n=" + str(n),
            trigger_at=datetime.datetime.now() + datetime.timedelta(seconds=10),
            interval=datetime.timedelta(seconds=10),
            target_evl="dev_trm_reminder",
            data=dict(n=n)
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
    $ num = reminder.data["n"]
    m 1hua "Got a reminder for you! Number is... [num]!"
    return


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="dev_trm_list",
            prompt="LIST REMINDERS",
            category=["DEV"],
            pool=True,
            unlocked=True
        ),
        code="EVE"
    )

label dev_trm_list:
    $ reminders = store.trm_reminder.get_reminders()
    if len(reminders) == 0:
        m 3hksdlb "Hehe, [player]... You have none so far~"
        return

    python:
        items = list()
        for key, rem in reminders.items():
            items.append((rem.prompt, rem, False, False))

    show monika at t21
    call screen mas_gen_scrollable_menu(items, mas_ui.SCROLLABLE_MENU_TXT_TALL_AREA, mas_ui.SCROLLABLE_MENU_XALIGN, ("Nevermind.", False, False, False, 0))
    show monika at t11

    if _return is not False:
        m 3eub "Okay, I'll remove it!"
        $ store.trm_reminder.dequeue_reminder(_return)
        return

    m 3eka "Oh, okay!"
    return