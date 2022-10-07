init 5 python in mas_bookmarks_derand:
    label_prefix_map["trm_topic_"] = label_prefix_map["monika_"]


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="trm_ev_reminder_delegate"
        ),
        code="EVE"
    )

label trm_ev_reminder_delegate:
    # TODO: Dialogue. On you, Gaby :>
    $ note = reminder.data["note"]
    m 1hua "Got a reminder for you! It says... [note]!"
    return


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="trm_topic_reminder_remove",
            prompt="Can you stop reminding me about something?",
            category=["misc"],
            pool=True,
            rules={"no_unlock": None}
        ),
        code="EVE"
    )

label trm_topic_reminder_remove:
    python:
        items = list()
        for key, rem in store.trm_reminder.get_reminders().items():
            items.append((renpy.substitute(rem.prompt), rem, False, False))

    show monika at t21
    call screen mas_gen_scrollable_menu(items, mas_ui.SCROLLABLE_MENU_TXT_TALL_AREA, mas_ui.SCROLLABLE_MENU_XALIGN, ("Nevermind.", False, False, False, 0))
    show monika at t11

    # TODO: Dialogue. This too, Gaby :}
    if _return is not False:
        m 3eub "Okay, I'll stop!"
        $ store.trm_reminder.dequeue_reminder(_return)

    else:
        m 3eka "Oh, okay."

    return


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="trm_topic_reminder_oneshot",
            prompt="Can you remind me about something?",
            category=["misc"],
            pool=True,
            unlocked=True
        ),
        code="EVE"
    )

label trm_topic_reminder_oneshot:
    # TODO: Dialogue. Go for it, Gaby :P
    m "Of course! Let me write it down so you won't forget what is it about..."

    label .set_note:
        python:
            note = mas_input(
                "How should I remind you about it?",
                allow="abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ-_0123456789",
                length=32,
                screen_kwargs={"use_return_button": True}
            )

        if note == "cancel_input":
            # User has clicked "nevermind".
            m "Oh, okay."
            return

        if "reminder " + note.lower() in store.trm_reminder.get_reminders():
            m "[player], I already have a reminder with note like this..."
            m "I can label it somehow else so you don't get confused with both of them!"
            jump .set_note

    m "Okay! Now pick when should I remind you about it."

    python:
        items = [
            ("In 5 minutes", datetime.timedelta(seconds=300), False, False),
            ("In 10 minutes", datetime.timedelta(seconds=600), False, False),
            ("In 15 minutes", datetime.timedelta(seconds=900), False, False),
            ("In 30 minutes", datetime.timedelta(seconds=1800), False, False),
            ("In 1 hour", datetime.timedelta(seconds=3600), False, False),
            ("In 2 hours", datetime.timedelta(seconds=7200), False, False),
            ("In 3 hours", datetime.timedelta(seconds=10800), False, False),
            ("In 6 hours", datetime.timedelta(seconds=21600), False, False),
            ("In 12 hours", datetime.timedelta(seconds=43200), False, False),
            ("In 24 hours", datetime.timedelta(days=1), False, False)
        ]

    show monika at t21
    call screen mas_gen_scrollable_menu(items, mas_ui.SCROLLABLE_MENU_TXT_TALL_AREA, mas_ui.SCROLLABLE_MENU_XALIGN, ("Nevermind.", False, False, False, 4))
    show monika at t11

    if _return is False:
        # User has clicked "nevermind".
        m "Oh, okay."
        return

    m "Okay! I'll be sure not to forget~"

    python:
        store.trm_reminder.queue_reminder(trm_Reminder(
            key="reminder " + note.lower(),
            prompt=note,
            trigger_at=datetime.datetime.now() + _return,
            target_evl="trm_ev_reminder_delegate",
            data=dict(note=note)
        ))
    return


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="trm_topic_reminder_recurring",
            prompt="Can you set a reminder for me?",
            category=["misc"],
            pool=True,
            unlocked=True
        ),
        code="EVE"
    )

label trm_topic_reminder_recurring:
    # TODO: Dialogue. Final part, Gaby c:
    m "Of course! Let me write it down so you won't forget what is it about..."

    label .set_note:
        python:
            note = mas_input(
                "How should I remind you about it?",
                allow="abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ-_0123456789",
                length=32,
                screen_kwargs={"use_return_button": True}
            )

        if note == "cancel_input":
            # User has clicked "nevermind".
            m "Oh, okay."
            return

        if "reminder " + note.lower() in store.trm_reminder.get_reminders():
            m "[player], I already have a reminder with note like this..."
            m "I can label it somehow else so you don't get confused with both of them!"
            jump .set_note

    m "Okay! Now pick when should how often should remind you about it."

    python:
        items = [
            ("Every 5 minutes", datetime.timedelta(seconds=300), False, False),
            ("Every 10 minutes", datetime.timedelta(seconds=600), False, False),
            ("Every 15 minutes", datetime.timedelta(seconds=900), False, False),
            ("Every 30 minutes", datetime.timedelta(seconds=1800), False, False),
            ("Every 1 hour", datetime.timedelta(seconds=3600), False, False),
            ("Every 2 hours", datetime.timedelta(seconds=7200), False, False),
            ("Every 3 hours", datetime.timedelta(seconds=10800), False, False),
            ("Every 6 hours", datetime.timedelta(seconds=21600), False, False),
            ("Every 12 hours", datetime.timedelta(seconds=43200), False, False),
            ("Every 24 hours", datetime.timedelta(days=1), False, False)
        ]

    show monika at t21
    call screen mas_gen_scrollable_menu(items, mas_ui.SCROLLABLE_MENU_TXT_TALL_AREA, mas_ui.SCROLLABLE_MENU_XALIGN, ("Nevermind.", False, False, False, 4))
    show monika at t11

    if _return is False:
        # User has clicked "nevermind".
        m "Oh, okay."
        return

    m "Okay! I'll be sure not to forget~"

    python:
        store.trm_reminder.queue_reminder(trm_Reminder(
            key="reminder " + note.lower(),
            prompt=note,
            trigger_at=datetime.datetime.now() + _return,
            interval=_return,
            target_evl="trm_ev_reminder_delegate",
            data=dict(note=note)
        ))
    return