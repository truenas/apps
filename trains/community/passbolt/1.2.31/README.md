# Passbolt

[Passbolt](https://www.passbolt.com) is a security-first, open source password manager

## Register admin user

Connect to the container's shell and run the following command replacing the
values (`user@example.com`, `first_name`, `last_name`) with your own values.

```shell
/usr/share/php/passbolt/bin/cake passbolt register_user -r admin -u user@example.com -f first_name -l last_name
```
