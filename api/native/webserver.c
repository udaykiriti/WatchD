#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <pthread.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <errno.h>
#include <signal.h>
#include <dlfcn.h>
#include <time.h>

#define PORT 8000
#define BUFFER_SIZE 8192
#define MAX_CLIENTS 50
#define WEB_ROOT "../web"

typedef char* (*metrics_fn)(void);
typedef void (*free_fn)(char*);

static void* rust_lib = NULL;
static metrics_fn rust_get_metrics = NULL;
static free_fn rust_free_string = NULL;
static volatile int running = 1;

void handle_signal(int sig) {
    running = 0;
}

int load_rust_library() {
    const char* lib_path = "monitor/native/rust/target/release/libsysguard_monitor.so";
    rust_lib = dlopen(lib_path, RTLD_LAZY);
    if (!rust_lib) {
        fprintf(stderr, "Failed to load Rust library: %s\n", dlerror());
        return 0;
    }
    
    rust_get_metrics = (metrics_fn)dlsym(rust_lib, "rust_get_metrics_json");
    rust_free_string = (free_fn)dlsym(rust_lib, "rust_free_string");
    
    if (!rust_get_metrics || !rust_free_string) {
        fprintf(stderr, "Failed to load Rust functions\n");
        dlclose(rust_lib);
        return 0;
    }
    
    return 1;
}

char* get_content_type(const char* path) {
    if (strstr(path, ".html")) return "text/html";
    if (strstr(path, ".js")) return "application/javascript";
    if (strstr(path, ".css")) return "text/css";
    if (strstr(path, ".json")) return "application/json";
    return "text/plain";
}

void send_file(int client_fd, const char* filepath) {
    char full_path[512];
    snprintf(full_path, sizeof(full_path), "%s/%s", WEB_ROOT, filepath);
    
    int fd = open(full_path, O_RDONLY);
    if (fd < 0) {
        const char* response = 
            "HTTP/1.1 404 Not Found\r\n"
            "Content-Length: 9\r\n\r\n"
            "Not Found";
        send(client_fd, response, strlen(response), 0);
        return;
    }
    
    struct stat st;
    fstat(fd, &st);
    
    char header[512];
    snprintf(header, sizeof(header),
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: %s\r\n"
        "Content-Length: %ld\r\n"
        "Connection: close\r\n\r\n",
        get_content_type(filepath), st.st_size);
    
    send(client_fd, header, strlen(header), 0);
    
    char buffer[BUFFER_SIZE];
    ssize_t bytes;
    while ((bytes = read(fd, buffer, sizeof(buffer))) > 0) {
        send(client_fd, buffer, bytes, 0);
    }
    
    close(fd);
}

void send_metrics_json(int client_fd) {
    char* metrics = rust_get_metrics();
    if (!metrics) {
        const char* error = "{\"error\":\"Failed to get metrics\"}";
        char response[256];
        snprintf(response, sizeof(response),
            "HTTP/1.1 500 Internal Server Error\r\n"
            "Content-Type: application/json\r\n"
            "Content-Length: %ld\r\n\r\n%s",
            strlen(error), error);
        send(client_fd, response, strlen(response), 0);
        return;
    }
    
    char header[256];
    snprintf(header, sizeof(header),
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: application/json\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        "Content-Length: %ld\r\n\r\n",
        strlen(metrics));
    
    send(client_fd, header, strlen(header), 0);
    send(client_fd, metrics, strlen(metrics), 0);
    
    rust_free_string(metrics);
}

void* handle_websocket_client(void* arg) {
    int client_fd = *(int*)arg;
    free(arg);
    
    const char* ws_accept = 
        "HTTP/1.1 101 Switching Protocols\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        "Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=\r\n\r\n";
    
    send(client_fd, ws_accept, strlen(ws_accept), 0);
    
    while (running) {
        char* metrics = rust_get_metrics();
        if (metrics) {
            size_t len = strlen(metrics);
            unsigned char frame[10];
            int header_len;
            
            frame[0] = 0x81;
            if (len <= 125) {
                frame[1] = len;
                header_len = 2;
            } else if (len <= 65535) {
                frame[1] = 126;
                frame[2] = (len >> 8) & 0xFF;
                frame[3] = len & 0xFF;
                header_len = 4;
            } else {
                frame[1] = 127;
                for (int i = 0; i < 8; i++) {
                    frame[2 + i] = (len >> (56 - i * 8)) & 0xFF;
                }
                header_len = 10;
            }
            
            if (send(client_fd, frame, header_len, 0) <= 0) break;
            if (send(client_fd, metrics, len, 0) <= 0) break;
            
            rust_free_string(metrics);
        }
        sleep(1);
    }
    
    close(client_fd);
    return NULL;
}

void handle_client(int client_fd) {
    char buffer[BUFFER_SIZE];
    ssize_t bytes = recv(client_fd, buffer, sizeof(buffer) - 1, 0);
    
    if (bytes <= 0) {
        close(client_fd);
        return;
    }
    
    buffer[bytes] = '\0';
    
    if (strstr(buffer, "Upgrade: websocket")) {
        int* fd_ptr = malloc(sizeof(int));
        *fd_ptr = client_fd;
        pthread_t thread;
        pthread_create(&thread, NULL, handle_websocket_client, fd_ptr);
        pthread_detach(thread);
        return;
    }
    
    if (strncmp(buffer, "GET /health", 11) == 0) {
        send_metrics_json(client_fd);
    } else if (strncmp(buffer, "GET /dashboard.js", 17) == 0) {
        send_file(client_fd, "dashboard.js");
    } else if (strncmp(buffer, "GET /", 5) == 0) {
        send_file(client_fd, "index.html");
    } else {
        const char* response = "HTTP/1.1 400 Bad Request\r\n\r\n";
        send(client_fd, response, strlen(response), 0);
    }
    
    close(client_fd);
}

int main() {
    signal(SIGINT, handle_signal);
    signal(SIGTERM, handle_signal);
    
    if (!load_rust_library()) {
        fprintf(stderr, "Failed to load Rust library. Build it first: ./buildnative.sh\n");
        return 1;
    }
    
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("Socket creation failed");
        return 1;
    }
    
    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    
    struct sockaddr_in addr = {0};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(PORT);
    
    if (bind(server_fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("Bind failed");
        close(server_fd);
        return 1;
    }
    
    if (listen(server_fd, MAX_CLIENTS) < 0) {
        perror("Listen failed");
        close(server_fd);
        return 1;
    }
    
    printf("\n");
    printf("  ╔════════════════════════════════════╗\n");
    printf("  ║   SysGuard Native Web Server      ║\n");
    printf("  ║   High Performance C Backend      ║\n");
    printf("  ╚════════════════════════════════════╝\n");
    printf("\n");
    printf("  [OK] Server started on port %d\n", PORT);
    printf("  [OK] Web interface: http://localhost:%d\n", PORT);
    printf("  [OK] Health endpoint: http://localhost:%d/health\n", PORT);
    printf("  [OK] Press Ctrl+C to stop\n\n");
    
    while (running) {
        struct sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);
        
        int client_fd = accept(server_fd, (struct sockaddr*)&client_addr, &client_len);
        if (client_fd < 0) {
            if (running) perror("Accept failed");
            continue;
        }
        
        handle_client(client_fd);
    }
    
    printf("\n[OK] Server shutting down...\n");
    close(server_fd);
    if (rust_lib) dlclose(rust_lib);
    
    return 0;
}
