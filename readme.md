# Poke

An interactive environment for probabilistic programming.

![Screencast 1](https://github.com/stuhlmueller/poke/raw/master/media/poke-flip.gif)

![Screencast 2](https://github.com/stuhlmueller/poke/raw/master/media/poke-geom.gif)

Note: This tool is barely functional and depends on a number of software packages that are themselves barely functional. I use this for probabilistic programming tutorials, but it is far from mature and probably will never be.

## Usage

First, adjust `settings.py` and `settings.ss`.

To start the file monitor, run:

    $ python ./observer.py 

To start the user interface, run:

    $ python ./ui.py

## Requirements

- [python-tools](https://github.com/stuhlmueller/python-tools)
- [scheme-tools](https://github.com/stuhlmueller/scheme-tools)
- [enthought python](http://enthought.com/products/epd.php)
- [watchdog](http://packages.python.org/watchdog/)
- [bher](http://projects.csail.mit.edu/church/wiki/Installing_Bher)

## References

- Inspiration: Bred Victor's talk [Inventing on Principle](https://vimeo.com/36579366).
- `hashable.py` is based on [this StackOverflow post](http://stackoverflow.com/questions/1611797/using-non-hashable-python-objects-as-keys-in-dictionaries)
- `barchart.py` is based on [this chaco mailing list posting](https://mail.enthought.com/pipermail/chaco-users/2009-October/001422.html)
- `read-source` in `church-loop.ss` is based on `bher/church-compiler.ss`
