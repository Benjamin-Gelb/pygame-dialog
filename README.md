# PyDialog

Pygame Dialog (PyDialog) is a hobby project for building menus in the pygame engine.

Feature goals pre v1.0.0 is to:
- Responsive Dialog Window
- Scrolling text
- Option Navigation
- Buttons
- Design Controls

Feel free to make suggestions or contributions.


Basic Example -> Opening and closing a dialog box when 'h' is pressed:

```python
# init pygame
screen = 
dialog_config = SnapToBottom(screen=screen, height=40, padding_y=10, padding_x=10)
dialog = Dialog(dialog_config)


open_condition = False
while True:
    # ...
    for events in pygame.events.get():
        # Game code...
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:
                if dialog.is_open():
                    open_condition = False # close if open
                else:
                    open_condition = True # open if closed

        if open_condition:
            dialog.open() # Open Dialog
            dialog.write("Hello Dialog.") # Write text to dialog box.
        if not open_condition and dialog.is_open():
            dialog.clear() # empty text
            dialog.close() # close dialog box
    
    dialog.render(screen) 
    
```