CC = gcc
CFLAGS = -Wall -O2 -pthread
LDFLAGS = -ldl -pthread
TARGET = webserver
SRC = webserver.c

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC) $(LDFLAGS)
	@echo "[OK] Native web server compiled"

clean:
	rm -f $(TARGET)

.PHONY: all clean
