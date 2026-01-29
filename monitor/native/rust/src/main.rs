use sysguard_monitor::get_all_metrics;
use std::env;

fn main() {
    let args: Vec<String> = env::args().collect();
    let limit = if args.len() > 1 {
        args[1].parse::<usize>().unwrap_or(5)
    } else {
        5
    };
    
    let metrics = get_all_metrics(limit);
    
    println!("{}", serde_json::to_string_pretty(&metrics).unwrap());
}
