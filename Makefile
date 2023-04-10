install_font:
	wget  https://www.wfonts.com/download/data/2014/06/09/atari-st-8x16-system-font/AtariST8x16SystemFont.ttf


run:
	sudo ./rgb_panel_animate.py  --led-cols=64  --led-rows=64 --led-slowdown-gpio=2 --led-chain=2 --text="Hello World!"	



