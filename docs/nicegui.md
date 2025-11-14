NiceGUI Documentation:

navigation bar:
https://github.com/zauberzeug/nicegui/discussions/1715

icons:
https://fonts.google.com/icons


## colors
https://stackoverflow.com/questions/75269412/where-and-how-can-i-define-the-primary-and-secondary-colors
https://quasar.dev/style/color-palette/



## native mode
Some fixes for native mode: github.com/zauberzeug/nicegui/issues/1841

```python
import multiprocessing
multiprocessing.set_start_method("spawn", force=True)

```

# native mode:
# see: https://github.com/zauberzeug/nicegui/issues/1841
# sudo apt install gobject-introspection libgirepository-1.0-dev libcairo2-dev

