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
    $ note = renpy.substitute(reminder.prompt)
    m 7eub "Hey [player]!"
    m 7eua "I've got a reminder for you! "
    extend 7dub "It says... [note]!"
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
        for key, rem in store._trm_reminder.get_reminders().items():
            if rem.remaining.total_seconds() <= 0:
                eta = ""

            else:
                hours = int(rem.remaining.total_seconds() // 3600)
                minutes = int(rem.remaining.total_seconds() // 60)

                if hours > 0:
                    tn = hours
                    tu = "小时"

                elif minutes > 0:
                    tn = minutes
                    tu = "分钟"

                else:
                    tn = int(rem.remaining.total_seconds())
                    tu = "秒"

                eta = " (在 {0} {1} 后".format(tn, tu)
                if tn != 1:
                    eta += ""

                if rem.interval is not None:
                    hours = int(rem.interval.total_seconds() // 3600)
                    minutes = int(rem.interval.total_seconds() // 60)

                    if hours > 0:
                        rn = hours
                        ru = "小时"

                    elif minutes > 0:
                        rn = minutes
                        ru = "分钟"

                    else:
                        rn = int(rem.interval.total_seconds())
                        ru = "秒"

                    eta += ", 每 {0} {1}".format(rn, ru)
                    if rn != 1:
                        eta += ""

                eta += ")"

            items.append((renpy.substitute(rem.prompt) + eta, rem, False, False))

    show monika at t21
    call screen mas_gen_scrollable_menu(items, mas_ui.SCROLLABLE_MENU_TXT_TALL_AREA, mas_ui.SCROLLABLE_MENU_XALIGN, ("Nevermind.", False, False, False, 0))
    show monika at t11

    if _return is not False:
        m 3eub "Okay, I'll stop!"
        $ store._trm_reminder.dequeue_reminder(_return)
        if len(items) == 1:
            $ mas_hideEVL("trm_topic_reminder_remove", "EVE", lock=True)

    else:
        m 3eka "Oh, okay."

    return


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="trm_topic_reminder_oneshot",
            prompt="Can you create a timer for me?",
            category=["misc"],
            pool=True,
            unlocked=True
        ),
        code="EVE"
    )

label trm_topic_reminder_oneshot:
    call trm_topic_reminder_create(recurring=False)
    return


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="trm_topic_reminder_recurring",
            prompt="Can you set a recurring reminder for me?",
            category=["misc"],
            pool=True,
            unlocked=True
        ),
        code="EVE"
    )

label trm_topic_reminder_recurring:
    call trm_topic_reminder_create(recurring=True)
    return


label trm_topic_reminder_create(recurring):
    m 7dub "Of course! Let me write it down so I don't forget it..."

    label .set_note:
        python:
            note = mas_input(
                "需要我帮你记住什么呢?",
                #allow="abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ-_0123456789",
                length=32,
                screen_kwargs={"use_return_button": True}
            )

        if note == "":
            m 3hka "[player], you didn't write anything!"
            m 1hua "Try again~"
            jump .set_note

        elif note == "cancel_input":
            m 3eka "Oh, okay."
            return

        elif "reminder " + note.lower() in store._trm_reminder.get_reminders():
            m 3eka "[player], I already have a reminder with a note like this..."
            m 3ekb "I can label it something else so you don't get confused with both of them!"
            jump .set_note

    if recurring:
        $ quip = "好的! 现在告诉我多久提醒你一次."
    else:
        $ quip = "好的! 现在告诉我多久以后提醒你."
    m 3eub "[quip]"

    python:
        item_prefix = "每 " if recurring else "在 "
        item_aftfix = "" if recurring else "后"
        items = [
            (item_prefix + "5 分钟" + item_aftfix, datetime.timedelta(seconds=300), False, False),
            (item_prefix + "10 分钟" + item_aftfix, datetime.timedelta(seconds=600), False, False),
            (item_prefix + "15 分钟" + item_aftfix, datetime.timedelta(seconds=900), False, False),
            (item_prefix + "30 分钟" + item_aftfix, datetime.timedelta(seconds=1800), False, False),
            (item_prefix + "1 小时" + item_aftfix, datetime.timedelta(seconds=3600), False, False),
            (item_prefix + "2 小时" + item_aftfix, datetime.timedelta(seconds=7200), False, False),
            (item_prefix + "3 小时" + item_aftfix, datetime.timedelta(seconds=10800), False, False),
            (item_prefix + "6 小时" + item_aftfix, datetime.timedelta(seconds=21600), False, False),
            (item_prefix + "12 小时" + item_aftfix, datetime.timedelta(seconds=43200), False, False),
            (item_prefix + "24 小时" + item_aftfix, datetime.timedelta(days=1), False, False)
        ]

    show monika at t21
    call screen mas_gen_scrollable_menu(items, mas_ui.SCROLLABLE_MENU_TXT_TALL_AREA, mas_ui.SCROLLABLE_MENU_XALIGN, ("Nevermind.", False, False, False, 4))
    show monika at t11

    if _return is False:
        m 3eka "Oh, okay."
        return

    m 1hua "Okay! I'll be sure not to forget~"

    python:
        store._trm_reminder.queue_reminder(store._trm_reminder.Reminder(
            key="reminder " + note.lower(),
            prompt=note,
            trigger_at=datetime.datetime.now() + _return,
            interval=_return if recurring else None,
            target_evl="trm_ev_reminder_delegate"
        ))

    $ mas_showEVL("trm_topic_reminder_remove", "EVE", unlock=True)
    return
