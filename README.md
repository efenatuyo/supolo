# supolo
a fast discord nuke bot based package

in early stages !!

example of response
`
{'success': True, 'time_taken': 0.24078199997893535, 'total_ratelimits': 0, 'info': {}}
`

### important
I suggest to leave `skipOnRatelimit` false on bigger tasks like mass kick, mass ban etc due to these endpoints ratelimiting fast but for a short time. You can modify `ratelimitCooldown` in seconds (can also be 0 not suggested)
