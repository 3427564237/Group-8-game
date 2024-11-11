import time
import psutil

class PerformanceMonitor:
    def __init__(self):
        self.fps_stats = []
        self.memory_usage = []
        self.frame_start_time = 0
        self.frame_count = 0
        self.last_fps_update = time.time()
        self.metrics_update_interval = 1.0
        
        self.performance_metrics = {
            'fps': [],
            'memory_usage': [],
            'frame_times': []
        }
        
        self.last_metrics_update = time.time()
    
    def start_frame(self):
        """Start frame timing"""
        self.frame_start_time = time.time()
        self.frame_count += 1
    
    def end_frame(self):
        """End frame timing and update metrics"""
        frame_time = time.time() - self.frame_start_time
        self.performance_metrics['frame_times'].append(frame_time)
        
        current_time = time.time()
        if current_time - self.last_fps_update >= 1.0:
            fps = self.frame_count / (current_time - self.last_fps_update)
            self.performance_metrics['fps'].append(fps)
            self.frame_count = 0
            self.last_fps_update = current_time
            
        self.update_performance_metrics()
    
    def update_performance_metrics(self):
        """Update performance metrics"""
        current_time = time.time()
        if current_time - self.last_metrics_update >= self.metrics_update_interval:
            self.performance_metrics['memory_usage'].append(self.get_memory_usage())
            
            # Keep only recent samples
            for key in self.performance_metrics:
                if len(self.performance_metrics[key]) > 100:
                    self.performance_metrics[key] = self.performance_metrics[key][-100:]
            
            self.last_metrics_update = current_time
    
    def get_memory_usage(self):
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0 