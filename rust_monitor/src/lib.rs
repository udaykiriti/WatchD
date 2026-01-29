use serde::{Deserialize, Serialize};
use sysinfo::{CpuExt, System, SystemExt, ProcessExt, PidExt};

#[derive(Serialize, Deserialize, Debug)]
pub struct CpuMetrics {
    pub usage_percent: f32,
    pub cores_logical: usize,
    pub load_avg_1: f64,
    pub load_avg_5: f64,
    pub load_avg_15: f64,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct MemoryMetrics {
    pub total_mb: u64,
    pub used_mb: u64,
    pub available_mb: u64,
    pub percent: f64,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ProcessInfo {
    pub pid: u32,
    pub name: String,
    pub cpu_percent: f32,
    pub memory_mb: u64,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct SystemMetrics {
    pub cpu: CpuMetrics,
    pub memory: MemoryMetrics,
    pub top_processes: Vec<ProcessInfo>,
}

pub fn get_cpu_metrics(sys: &System) -> CpuMetrics {
    let load_avg = System::load_average();
    
    CpuMetrics {
        usage_percent: sys.global_cpu_info().cpu_usage(),
        cores_logical: sys.cpus().len(),
        load_avg_1: load_avg.one,
        load_avg_5: load_avg.five,
        load_avg_15: load_avg.fifteen,
    }
}

pub fn get_memory_metrics(sys: &System) -> MemoryMetrics {
    let total = sys.total_memory();
    let used = sys.used_memory();
    let available = sys.available_memory();
    
    MemoryMetrics {
        total_mb: total / 1024 / 1024,
        used_mb: used / 1024 / 1024,
        available_mb: available / 1024 / 1024,
        percent: (used as f64 / total as f64) * 100.0,
    }
}

pub fn get_top_processes(sys: &System, limit: usize) -> Vec<ProcessInfo> {
    let mut processes: Vec<ProcessInfo> = sys
        .processes()
        .iter()
        .map(|(pid, process)| ProcessInfo {
            pid: pid.as_u32(),
            name: process.name().to_string(),
            cpu_percent: process.cpu_usage(),
            memory_mb: process.memory() / 1024 / 1024,
        })
        .collect();
    
    // Sort by CPU usage
    processes.sort_by(|a, b| b.cpu_percent.partial_cmp(&a.cpu_percent).unwrap());
    
    processes.truncate(limit);
    processes
}

pub fn get_all_metrics(limit: usize) -> SystemMetrics {
    let mut sys = System::new_all();
    sys.refresh_all();
    
    // Sleep briefly to get accurate CPU usage
    std::thread::sleep(std::time::Duration::from_millis(200));
    sys.refresh_cpu();
    
    SystemMetrics {
        cpu: get_cpu_metrics(&sys),
        memory: get_memory_metrics(&sys),
        top_processes: get_top_processes(&sys, limit),
    }
}

#[no_mangle]
pub extern "C" fn rust_get_metrics_json(limit: usize) -> *mut libc::c_char {
    let metrics = get_all_metrics(limit);
    let json = serde_json::to_string(&metrics).unwrap_or_else(|_| "{}".to_string());
    
    std::ffi::CString::new(json)
        .unwrap()
        .into_raw()
}

#[no_mangle]
pub extern "C" fn rust_free_string(s: *mut libc::c_char) {
    unsafe {
        if !s.is_null() {
            let _ = std::ffi::CString::from_raw(s);
        }
    }
}
