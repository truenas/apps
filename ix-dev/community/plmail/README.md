# plMail

[plMail](https://github.com/karatektus/pl_mail) is a self-hosted mail client with a calendar beside it.
It connects to the mailboxes you already have (IMAP, Gmail, Outlook), syncs them into its own
PostgreSQL database and shows them in one inbox. It is not a mail server.

Everything plMail stores, including the generated key that encrypts mailbox passwords,
lives in the single data storage configured at install. Back that storage up.
