import unittest

import telebot

from common import getConfig
from im.tgchat import TgBot, TgChat
    

class TestBot(unittest.TestCase):
    
    def setUp(self):
        self.config = getConfig()

    def test_matching(self):
        self.skipTest("for now")
        chat = TgChat(None, "ut", 3)

        text = r"""
Here's an example using a non-hashable type "MyType":

```go
type MyType struct {
    // fields and methods of your type
}
```

and

```python
if __name__ == '__main__':
    print('hello world')
```


Alternatively, if you still want to use the non-hashable type as the key itself, you might consider using a different data structure, like a slice or a custom implementation of a hash table that can handle non-hashable keys.        
"""

        newText = chat.escape(text)
        print(newText)
            
    def test_matching_emphasized(self):
        text = r"""        In this example, we get `\b\w+\b`."""

        chat = TgChat(None, "ut", 4)
        newText = chat.escape(text)

    def test_matching_nested(self):
        self.skipTest("for now")
        text = r"""
```In this example, we convert the `slice` key to a string using `fmt.Sprintf` and use that string as the key in the map.```"""

        chat = TgChat(None, "ut", 3)
        newText = chat.escape(text)
        
        

if __name__ == '__main__':
    unittest.main()