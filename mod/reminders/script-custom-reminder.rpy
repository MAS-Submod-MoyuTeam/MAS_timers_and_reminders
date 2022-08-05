## custom reminder goes here! let me know whenever you need dialogue or expressions! or any help at all!!!!

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="otter_reminder_new",
            prompt="Can you remind me about something?",
            pool=True,
            unlocked=True
        ),
        code="EVE"
    )

label otter_reminder_new:
    m "Sure! What did you want me to remind you about?"

    python:
        note = mas_input(
            "What to remind about?",
            length=30,
            screen_kwargs={"use_return_button": True}
        ).strip(' \t\n\r')

        orm_addTarget(orm_Reminder(
            key=note,
            event_label="otter_reminder_callback",
            trigger_at=datetime.datetime.now() + datetime.timedelta(seconds=10),
            data=dict(note=note)
        ))

    m "Okay! I'll be sure to remind you about it~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="otter_reminder_callback"
        ),
        code="EVE"
    )

label otter_reminder_callback:
    m "[player], you wanted me to remind you about something!"
    m "Lemme read the note..."
    $ note = orm_target.data["note"]
    m "'[note]'"
    m "Hope it helped you, [mas_get_player_nickname()]~"
    return
    
    
    ##prompt for when to fire reminder
    
    "And when do you want me to remind you?"
    
    "In 5 minutes":
    "In 30 minutes":
    "In 1 hour":
    "In 6 hours":
    "Tomorrow":
