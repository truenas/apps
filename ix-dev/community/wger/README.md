# Wger

[Wger](https://wger.de) is a self hosted FLOSS fitness/workout, nutrition and weight tracker.

## Upgrading from 2.5

### JWT Key Pair (replaces Signing Key)

In 2.6, `SIGNING_KEY` is replaced by a proper RSA key pair (`JWT_PRIVATE_KEY` and `JWT_PUBLIC_KEY`).
When upgrading, your old `signing_key` value is automatically migrated to `jwt_private_key`,
but you **must** generate a new key pair and update both fields.

To generate a new key pair, run the following from the TrueNAS shell (replace the project name with your own):

```bash
docker compose exec web ./manage.py generate-jwt-keys
```

Copy `JWT_PRIVATE_KEY` and `JWT_PUBLIC_KEY` from the output into the corresponding fields in the app settings.

### Removed REST API Endpoints

The following endpoints have been removed in 2.6:

| Removed endpoint | Replacement |
|---|---|
| `/api/v2/login/` | `/allauth/app/v1/auth/login` |
| `/api/v2/register/` | `/allauth/app/v1/auth/signup` |
| `/api/v2/token` | Use the **API key** page in user settings to mint a long-lived token |

If you have scripts or integrations using these endpoints, update them accordingly.

### UUID Primary Keys

The ID type for several models changed from integer to UUID string. This affects the following endpoints:

- `/api/v2/measurement-category/`
- `/api/v2/measurement/`
- `/api/v2/nutritionplan/` and `/api/v2/nutritionplaninfo/`
- `/api/v2/meal/`
- `/api/v2/mealitem/`
- `/api/v2/nutritiondiary/`
- `/api/v2/workoutsession/`
- `/api/v2/workoutlog/`

Update any scripts or integrations that store or compare these IDs.

### Powersync (Optional — Offline Mobile Support)

The new offline mode in the wger mobile app requires a PowerSync service. This is an optional
advanced setup. To enable it, run the following from the TrueNAS shell once after upgrading:

```bash
docker compose exec web ./manage.py setup-powersync-storage
```

For full administration details see the [PowerSync docs](https://wger.readthedocs.io/en/latest/administration/powersync.html).

### Social Login and Two-Factor Authentication

wger 2.6 adds support for social login providers (Google, Facebook, etc.) and two-factor
authentication (security codes, passkeys).

- [Social auth setup](https://wger.readthedocs.io/en/latest/administration/social_auth.html)
- [MFA setup](https://wger.readthedocs.io/en/latest/administration/mfa.html)

> **Note:** Due to the allauth changes you will need to re-login on the website after upgrading.
