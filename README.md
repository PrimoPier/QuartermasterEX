# Version 0.2.0
This second release of QuartermasterEX is the first major update in the bot's development life cycle, and establishes much of its primary functionality. The bot at this point in time is considered to be in closed alpha testing.

### New Commands
```
/verify
/view [username]
/award [user] [award] [description]
/help
```

### Commands Criteria
- `/award` is currently restricted to HIGHCOMM.
- `/view` will be met with an error message if attempting to view an unverified member's awards.
- The commands `/verify`, `/view`, `/award-data [view]`, and `/help` may now be used by anybody regardless of role.

### Other Updates
- Every response by the bot save for back end errors regarding the MySQL server will now have a unique embed.
- Confirmation embeds have been added for any command which directly affects the database or a user.
- A `date_awarded` column has been added to keep track of when a user was given an award. This can be seen by the `/view` command.
- `/award` has an optional `description` option to allow those distributing the award to entail the reason for the award.
- Officers may award multiple users the same award at once given they provide their username separated by a space.
- If an officer wishes to remove an award from a user, they may use the optional `remove` action in `/award [user]` and set the value to `True`.

### Known Issues
> [!IMPORTANT]
> This section will be updated with discovered issues as alpha testing progresses.

- When distributing multiple awards at once, a confirmation will appear based on how many awards there are
