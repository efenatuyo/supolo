# supolo
a fast discord nuke bot based package

[![pypi](https://github.com/efenatuyo/supolo/actions/workflows/python-publish.yml/badge.svg)](https://github.com/efenatuyo/supolo/actions/workflows/python-publish.yml)

in early stages !!

example of response
`
{'success': True, 'time_taken': 0.24078199997893535, 'total_ratelimits': 0, 'info': {}}
`

### important
I suggest to leave `skipOnRatelimit` false on bigger tasks like mass kick, mass ban etc due to these endpoints ratelimiting fast but for a short time. You can modify `ratelimitCooldown` in seconds (can also be 0 not suggested)


```
pip install supolo
```

showcase (channel delete, channel create & channel spam)

https://github.com/efenatuyo/supolo/assets/113731512/2192bd40-16a8-44c4-911a-e37254719e60
