# Terraria TShock

[Terraria TShock](https://github.com/Pryaxis/TShock) provides Terraria servers with server-side characters, anti-cheat, and community management tools.

On the first run, you have to check the logs to get the server token. You will find something like this:

```text
Login before join enabled. Users may be prompted for an account specific password instead of a server password on connect.
Login using UUID enabled. Users automatically login via UUID.
A malicious server can easily steal a user's UUID. You may consider turning this option off if you run a public server.
TShock Notice: setup-code.txt is still present, and the code located in that file will be used.
To setup the server, join the game and type /setup 424041
This token will display until disabled by verification. (/setup)
```

Join the server and run `/setup <token>`
