/*
 * Fast Process Watcher in C
 * Minimal overhead system process monitoring
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dirent.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <time.h>

#define MAX_PROCESSES 1024
#define MAX_NAME_LEN 256
#define PROC_DIR "/proc"

typedef struct {
    int pid;
    char name[MAX_NAME_LEN];
    unsigned long utime;
    unsigned long stime;
    unsigned long vsize;
    long rss;
} ProcessInfo;

int is_numeric(const char *str) {
    while (*str) {
        if (*str < '0' || *str > '9')
            return 0;
        str++;
    }
    return 1;
}

int read_proc_stat(int pid, ProcessInfo *pinfo) {
    char path[256];
    char buffer[1024];
    FILE *fp;
    
    snprintf(path, sizeof(path), "/proc/%d/stat", pid);
    fp = fopen(path, "r");
    if (!fp)
        return -1;
    
    if (fgets(buffer, sizeof(buffer), fp) == NULL) {
        fclose(fp);
        return -1;
    }
    
    fclose(fp);
    
    char *start = strchr(buffer, '(');
    char *end = strrchr(buffer, ')');
    if (!start || !end)
        return -1;
    
    // Extract process name
    int name_len = end - start - 1;
    if (name_len >= MAX_NAME_LEN)
        name_len = MAX_NAME_LEN - 1;
    strncpy(pinfo->name, start + 1, name_len);
    pinfo->name[name_len] = '\0';
    pinfo->pid = pid;
    
    // Parse remaining fields
    sscanf(end + 2, "%*c %*d %*d %*d %*d %*d %*u %*u %*u %*u %*u %lu %lu %*d %*d %*d %*d %*d %*d %*u %lu %ld",
           &pinfo->utime, &pinfo->stime, &pinfo->vsize, &pinfo->rss);
    
    return 0;
}

int get_all_processes(ProcessInfo *processes, int max_count) {
    DIR *dir;
    struct dirent *entry;
    int count = 0;
    
    dir = opendir(PROC_DIR);
    if (!dir) {
        perror("opendir");
        return -1;
    }
    
    while ((entry = readdir(dir)) != NULL && count < max_count) {
        if (entry->d_type == DT_DIR && is_numeric(entry->d_name)) {
            int pid = atoi(entry->d_name);
            if (read_proc_stat(pid, &processes[count]) == 0) {
                count++;
            }
        }
    }
    
    closedir(dir);
    return count;
}

void print_process_info(const ProcessInfo *pinfo) {
    unsigned long total_time = pinfo->utime + pinfo->stime;
    unsigned long mem_kb = pinfo->rss * sysconf(_SC_PAGESIZE) / 1024;
    
    printf("PID: %-6d | Name: %-20s | CPU: %-10lu | Mem: %lu KB\n",
           pinfo->pid, pinfo->name, total_time, mem_kb);
}

int compare_cpu(const void *a, const void *b) {
    const ProcessInfo *pa = (const ProcessInfo *)a;
    const ProcessInfo *pb = (const ProcessInfo *)b;
    unsigned long ta = pa->utime + pa->stime;
    unsigned long tb = pb->utime + pb->stime;
    return (tb > ta) - (tb < ta);
}

int compare_mem(const void *a, const void *b) {
    const ProcessInfo *pa = (const ProcessInfo *)a;
    const ProcessInfo *pb = (const ProcessInfo *)b;
    return (pb->rss > pa->rss) - (pb->rss < pa->rss);
}

void print_usage(const char *prog) {
    fprintf(stderr, "Usage: %s [-n count] [-s sort_by]\n", prog);
    fprintf(stderr, "  -n count    : Number of processes to display (default: 10)\n");
    fprintf(stderr, "  -s sort_by  : Sort by 'cpu' or 'mem' (default: cpu)\n");
}

int main(int argc, char *argv[]) {
    ProcessInfo processes[MAX_PROCESSES];
    int count;
    int display_count = 10;
    int sort_by_mem = 0;
    int opt;
    
    while ((opt = getopt(argc, argv, "n:s:h")) != -1) {
        switch (opt) {
            case 'n':
                display_count = atoi(optarg);
                break;
            case 's':
                if (strcmp(optarg, "mem") == 0 || strcmp(optarg, "memory") == 0) {
                    sort_by_mem = 1;
                }
                break;
            case 'h':
                print_usage(argv[0]);
                return 0;
            default:
                print_usage(argv[0]);
                return 1;
        }
    }
    
    printf("=== System Process Monitor (C) ===\n");
    printf("Collecting process information...\n\n");
    
    count = get_all_processes(processes, MAX_PROCESSES);
    if (count < 0) {
        fprintf(stderr, "Failed to read processes\n");
        return 1;
    }
    
    // Sort processes
    if (sort_by_mem) {
        qsort(processes, count, sizeof(ProcessInfo), compare_mem);
        printf("Top %d processes by memory usage:\n\n", display_count);
    } else {
        qsort(processes, count, sizeof(ProcessInfo), compare_cpu);
        printf("Top %d processes by CPU usage:\n\n", display_count);
    }
    
    // Display top processes
    int to_display = (count < display_count) ? count : display_count;
    for (int i = 0; i < to_display; i++) {
        print_process_info(&processes[i]);
    }
    
    printf("\nTotal processes: %d\n", count);
    
    return 0;
}
