# FCaptcha

[FCaptcha](https://github.com/WebDecoy/FCaptcha) is a self-hosted CAPTCHA for web forms. The container includes the browser widget, verification API, and demo.

Generate two independent random secrets before installation. Use the verification secret in your application's backend only. Open the Demo portal after installation and follow the [FCaptcha quickstart](https://docs.webdecoy.com/fcaptcha/quickstart/) to wire up your first form. Use HTTPS for integrations with production websites.

This package runs a single FCaptcha container with process-local challenge and replay state. Restarting the container resets that state.
