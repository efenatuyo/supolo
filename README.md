# supolo - A Fast Discord Nuke Bot Package

![Build Status](https://github.com/efenatuyo/supolo/actions/workflows/python-publish.yml/badge.svg)

**supolo** is a powerful Discord nuke bot package designed for speed and efficiency. With this package, you can perform various actions on Discord servers quickly and easily.

## Installation

You can install **supolo** via pip:

```bash
pip install supolo
```

## Usage

### Example Response

Here's an example of a response you might get when using **supolo**:

```python
{'success': True, 'time_taken': 0.24078199997893535, 'total_ratelimits': 0, 'info': {}}
```

### docs

if you need help with any function and a example with it use 
```python
help(function))
```

### Important Note

When performing larger tasks like mass kicks or bans, it is suggested to leave `skipOnRatelimit` set to `false`. Discord endpoints may rate limit fast but for a short time. You can modify the `ratelimitCooldown` parameter in seconds (can also be set to 0, but it's not recommended).

## Showcase

Check out this showcase to see **supolo** in action, demonstrating channel deletion, channel creation, and channel spamming:

[![supolo Showcase](https://github.com/efenatuyo/supolo/assets/113731512/2192bd40-16a8-44c4-911a-e37254719e60)](https://github.com/efenatuyo/supolo/assets/113731512/2192bd40-16a8-44c4-911a-e37254719e60)
