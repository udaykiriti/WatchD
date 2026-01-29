CC = gcc
CFLAGS = -Wall -Wextra -O3 -std=c11
LDFLAGS = -lm

TARGETS = process_watcher cpu_monitor

all: $(TARGETS)

process_watcher: process_watcher.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

cpu_monitor: cpu_monitor.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

clean:
	rm -f $(TARGETS) *.o

install: $(TARGETS)
	@echo "Installing to /usr/local/bin (requires sudo)"
	sudo cp $(TARGETS) /usr/local/bin/

uninstall:
	sudo rm -f /usr/local/bin/process_watcher
	sudo rm -f /usr/local/bin/cpu_monitor

.PHONY: all clean install uninstall
