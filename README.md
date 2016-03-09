pysdl2-sdl2ui
=============

A library to make simple UI using pysdl2.

Introduction
------------

```python
class MyApp(sdl2ui.App):
    width = 256
    height = 224
    zoom = 3
    # NOTE: the fps you desire: less fps = less CPU usage
    fps = 30
    name = "My Application"
    # NOTE: order the handlers in what you want to display first
    default_handlers = [MainHandler, ListSelectorHandler, MenuHandler]
    default_resources = [('background', 'background.png')]


logging.basicConfig(level=logging.DEBUG)
MyApp.run(handlers=[sdl2ui.handler.DebuggerHandler])
```

Each handler will have three main methods: `init()`, `peek()` and `draw()`:

* `init()` is called as soon as the application is started (instantiated). You
  can set all kind of variables in your instance here before anything shows up.
* `peek()` is called at every frame. The capture of the input can be made here.
  If peek() returns True, sdl2ui will re-draw the whole screen (using all the
  active handlers.
* `render()` is called every time the application need to re-draw the screen.

### Examples

```python
class MainHandler(sdl2ui.Handler):
    def peek(self):
        if self.app.keys[sdl2.SDL_SCANCODE_D]:
            self.app.keys[sdl2.SDL_SCANCODE_D] = False
            # NOTE: toggle the debugger mode
            self.app.handlers[sdl2ui.handler.DebuggerHandler].toggle()
        elif self.app.keys[sdl2.SDL_SCANCODE_S]:
            self.app.keys[sdl2.SDL_SCANCODE_S] = False
            # NOTE: toggle the display of the menu and the list selector
            self.app.handlers[ListSelectorHandler].toggle()
            self.app.handlers[MenuHandler].toggle()
        elif self.app.keys[sdl2.SDL_SCANCODE_Q]:
            self.app.keys[sdl2.SDL_SCANCODE_Q] = False
            self.app.quit = True
        else:
            return False
        return True

    def render(self):
        self.app.draw('background', x=0, y=0)
```

```python
class MenuHandler(sdl2ui.Handler):
    highlight = (0x00, 0x00, 0xff, 0xff)
    line_space = 8
    default_active = False
    menu_actions = [
        ("Save", lambda x: x.save()),
        ("Load", lambda x: x.load()),
        ("Quit", lambda x: x.quit()),
    ]

    def init(self):
        self.select = 0

    def save(self):
        # TODO save()
        pass

    def load(self):
        # TODO load()
        pass

    def quit(self):
        self.app.quit = True

    def peek(self):
        if self.app.keys[sdl2.SDL_SCANCODE_UP]:
            self.app.keys[sdl2.SDL_SCANCODE_UP] = False
            self.select -= 1
            if self.select < 0:
                self.select = len(self.menu_actions) - 1
        elif self.app.keys[sdl2.SDL_SCANCODE_DOWN]:
            self.app.keys[sdl2.SDL_SCANCODE_DOWN] = False
            self.select += 1
            if self.select >= len(self.menu_actions):
                self.select = 0
        elif self.app.keys[sdl2.SDL_SCANCODE_RETURN]:
            self.app.keys[sdl2.SDL_SCANCODE_RETURN] = False
            _, func = self.menu_actions[self.select]
            func()
        else:
            return False
        return True

    def render(self):
        border = 10
        x, y = border, border
        for i, (label, _) in enumerate(self.menu_actions):
            if i == self.select:
                # NOTE: you can tint all future draw() and write() using the
                #       context self.app.tint(<tuple_rgba>)
                with self.app.tint(self.highlight):
                    self.app.write('font-6', x, y, label)
            else:
                # NOTE: the font-6 is a bitmap font built-in with the library
                self.app.write('font-6', x, y, label)
            y += self.line_space
```
