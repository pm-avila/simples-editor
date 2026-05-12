CC      = gcc
CFLAGS  = -std=c99 -Wall -Wextra -O2

.PHONY: all clean

all: simplesc

simplesc: simplesc.c
	$(CC) $(CFLAGS) -o simplesc simplesc.c

clean:
	rm -f simplesc
