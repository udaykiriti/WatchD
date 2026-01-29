/*
 * CPU Monitor in C
 * Lightweight CPU usage tracking
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

typedef struct {
    unsigned long user;
    unsigned long nice;
    unsigned long system;
    unsigned long idle;
    unsigned long iowait;
    unsigned long irq;
    unsigned long softirq;
} CpuStats;

int read_cpu_stats(CpuStats *stats) {
    FILE *fp = fopen("/proc/stat", "r");
    if (!fp) {
        perror("fopen");
        return -1;
    }
    
    char buffer[256];
    if (fgets(buffer, sizeof(buffer), fp) == NULL) {
        fclose(fp);
        return -1;
    }
    
    sscanf(buffer, "cpu %lu %lu %lu %lu %lu %lu %lu",
           &stats->user, &stats->nice, &stats->system, &stats->idle,
           &stats->iowait, &stats->irq, &stats->softirq);
    
    fclose(fp);
    return 0;
}

double calculate_cpu_usage(const CpuStats *prev, const CpuStats *curr) {
    unsigned long prev_idle = prev->idle + prev->iowait;
    unsigned long curr_idle = curr->idle + curr->iowait;
    
    unsigned long prev_total = prev->user + prev->nice + prev->system + 
                               prev_idle + prev->irq + prev->softirq;
    unsigned long curr_total = curr->user + curr->nice + curr->system + 
                               curr_idle + curr->irq + curr->softirq;
    
    unsigned long total_diff = curr_total - prev_total;
    unsigned long idle_diff = curr_idle - prev_idle;
    
    if (total_diff == 0) {
        return 0.0;
    }
    
    return (100.0 * (total_diff - idle_diff) / total_diff);
}

void print_cpu_stats(const CpuStats *stats, double usage) {
    printf("CPU Usage: %.2f%%\n", usage);
    printf("User:      %lu\n", stats->user);
    printf("System:    %lu\n", stats->system);
    printf("Idle:      %lu\n", stats->idle);
    printf("IOWait:    %lu\n", stats->iowait);
}

int main(int argc, char *argv[]) {
    CpuStats prev_stats, curr_stats;
    int interval = 1;
    int continuous = 0;
    
    if (argc > 1) {
        interval = atoi(argv[1]);
    }
    
    if (argc > 2 && strcmp(argv[2], "-c") == 0) {
        continuous = 1;
    }
    
    printf("=== CPU Monitor (C) ===\n\n");
    
    if (read_cpu_stats(&prev_stats) < 0) {
        fprintf(stderr, "Failed to read CPU stats\n");
        return 1;
    }
    
    do {
        sleep(interval);
        
        if (read_cpu_stats(&curr_stats) < 0) {
            fprintf(stderr, "Failed to read CPU stats\n");
            return 1;
        }
        
        double usage = calculate_cpu_usage(&prev_stats, &curr_stats);
        
        if (continuous) {
            printf("\033[2J\033[H");  // Clear screen
        }
        
        print_cpu_stats(&curr_stats, usage);
        printf("\n");
        
        prev_stats = curr_stats;
    } while (continuous);
    
    return 0;
}
