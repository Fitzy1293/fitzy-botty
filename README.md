# fitzy-botty
My discord bot. Uses PRAW to do things write now, want to get into the letterboxd API.

# Commands
`-top "subreddit" "number of posts (or leave it blank)"`\
`-copypasta (gets a random copypasta)`\
`-randpic "subreddit" (gets a random image from a sub)`\
`-commands (lists commands)`

# Example of getting the top 10 current posts in a subreddit
![Imgur Image](https://i.imgur.com/qFLHvQv.png)

# A continuously updating formatted log



```python3
#!/bin/env python3

import os
from time import sleep

while True:
    os.system('clear')
    os.system('cat completed.txt')
    sleep(.5)
```

![Imgur Image](https://i.imgur.com/a0f6u2S.png)
