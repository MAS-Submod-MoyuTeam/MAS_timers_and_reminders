# TODO: Translation updated at 2022-10-22 22:57

# game/Submods/Timers and Reminders/reminder_topics.rpy:16
translate chinese trm_ev_reminder_delegate_012974af:

    # m 7eub "Hey [player]!"
    m 7eub "嘿 [player]!"

# game/Submods/Timers and Reminders/reminder_topics.rpy:17
translate chinese trm_ev_reminder_delegate_30d0c7d7:

    # m 7eua "I've got a reminder for you! "
    m 7eua "我要提醒你一下!"

# game/Submods/Timers and Reminders/reminder_topics.rpy:18
translate chinese trm_ev_reminder_delegate_e41aef2b:

    # extend 7dub "It says... [note]!"
    extend 7dub "上面说... [note]!"

# game/Submods/Timers and Reminders/reminder_topics.rpy:91
translate chinese trm_topic_reminder_remove_45562a56:

    # m 3eub "Okay, I'll stop!"
    m 3eub "好好, 我会停下!"

# game/Submods/Timers and Reminders/reminder_topics.rpy:97
translate chinese trm_topic_reminder_remove_b7d1fb4d:

    # m 3eka "Oh, okay."
    m 3eka "哦, 好吧."

# game/Submods/Timers and Reminders/reminder_topics.rpy:139
translate chinese trm_topic_reminder_create_5cbf5379:

    # m 7dub "Of course! Let me write it down so I don't forget it..."
    m 7dub "当然!让我把它写下来这样就不会忘掉..."

# game/Submods/Timers and Reminders/reminder_topics.rpy:151
translate chinese trm_topic_reminder_create_set_note_bfc138e5:

    # m 3hka "[player], you didn't write anything!"
    m 3hka "[player], 你什么都没写!"

# game/Submods/Timers and Reminders/reminder_topics.rpy:152
translate chinese trm_topic_reminder_create_set_note_c0d02512:

    # m 1hua "Try again~"
    m 1hua "再试一下~"

# game/Submods/Timers and Reminders/reminder_topics.rpy:156
translate chinese trm_topic_reminder_create_set_note_b7d1fb4d:

    # m 3eka "Oh, okay."
    m 3eka "哦,好的."

# game/Submods/Timers and Reminders/reminder_topics.rpy:160
translate chinese trm_topic_reminder_create_set_note_958cb390:

    # m 3eka "[player], I already have a reminder with a note like this..."
    m 3eka "[player], 我已经有一个像这样的提示了..."

# game/Submods/Timers and Reminders/reminder_topics.rpy:161
translate chinese trm_topic_reminder_create_set_note_10e60243:

    # m 3ekb "I can label it something else so you don't get confused with both of them!"
    m 3ekb "我可以给它打一些别的标签,这样你就不会把它们搞混了"

# game/Submods/Timers and Reminders/reminder_topics.rpy:168
translate chinese trm_topic_reminder_create_set_note_049d2106:

    # m 3eub "[quip]"
    m 3eub "[quip]"

# game/Submods/Timers and Reminders/reminder_topics.rpy:190
translate chinese trm_topic_reminder_create_set_note_b7d1fb4d_1:

    # m 3eka "Oh, okay."
    m 3eka "哦, 好的."

# game/Submods/Timers and Reminders/reminder_topics.rpy:193
translate chinese trm_topic_reminder_create_set_note_663ef89b:

    # m 1hua "Okay! I'll be sure not to forget~"
    m 1hua "好的! 我不会忘掉它的~"

translate chinese python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="trm_topic_reminder_remove",
            prompt="有些事情你可以不用再提醒我了?",
            category=["其它"],
            pool=True,
            rules={"no_unlock": None}
        ),
        code="EVE"
    )
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="trm_topic_reminder_oneshot",
            prompt="你可以为我计时吗?",
            category=["其它"],
            pool=True,
            unlocked=True
        ),
        code="EVE"
    )
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="trm_topic_reminder_recurring",
            prompt="你可以定期提醒我一件事吗?",
            category=["其它"],
            pool=True,
            unlocked=True
        ),
        code="EVE"
    )
