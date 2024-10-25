from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Vertical, Horizontal, Grid
from textual.widgets import Header, Footer, Button, Static, RichLog, Input
from textual.reactive import reactive
from pythonping import ping
import asyncio
import speedtest
from datetime import datetime
from typing import List, Dict


class ConsoleLog(RichLog):
    """Simple console-like log widget"""
    def __init__(self):
        super().__init__()
        self.auto_scroll = True

class SpeedTestDisplay(Static):
    """Widget to display speedtest results"""
    download_speed = reactive(0.0)
    upload_speed = reactive(0.0)
    ping_latency = reactive(0.0)
    is_testing = reactive(False)
    
    def on_mount(self) -> None:
        """Initialize the display"""
        self.update("Speed Test Ready")
    
    def update_display(self) -> None:
        """Update the speedtest display"""
        if self.is_testing:
            self.update("Running speed test...")
        else:
            self.update(
                f"Download: {self.download_speed:.1f} Mbps\n"
                f"Upload: {self.upload_speed:.1f} Mbps\n"
                f"Latency: {self.ping_latency:.1f} ms"
            )
    
    async def run_speedtest(self) -> None:
        """Run speedtest"""
        self.is_testing = True
        self.update_display()
        
        try:
            st = speedtest.Speedtest()
            self.console = self.app.query_one(ConsoleLog)
            
            self.console.write("\nGetting best server...")
            st.get_best_server()
            
            self.console.write("Testing download speed...")
            download_speed = st.download() / 1_000_000  # Convert to Mbps
            self.download_speed = download_speed
            
            self.console.write("Testing upload speed...")
            upload_speed = st.upload() / 1_000_000  # Convert to Mbps
            self.upload_speed = upload_speed
            
            self.ping_latency = st.results.ping
            
            self.console.write(
                f"\nSpeed test results:\n"
                f"Download: {download_speed:.1f} Mbps\n"
                f"Upload: {upload_speed:.1f} Mbps\n"
                f"Latency: {self.ping_latency:.1f} ms"
            )
            
        except Exception as e:
            self.console.write(f"\nSpeed test error: {str(e)}")
            
        finally:
            self.is_testing = False
            self.update_display()

class StatsDisplay(Static):
    """Widget to display ping statistics"""
    total_pings = reactive(0)
    failed_pings = reactive(0)
    avg_ping = reactive(0.0)
    packet_loss = reactive(0.0)
    
    def update_stats(self, ping_time: float, success: bool) -> None:
        """Update running statistics"""
        self.total_pings += 1
        if not success:
            self.failed_pings += 1
        else:
            # Update running average
            old_total = self.avg_ping * (self.total_pings - 1)
            self.avg_ping = (old_total + ping_time) / self.total_pings
        
        # Calculate packet loss percentage
        self.packet_loss = (self.failed_pings / self.total_pings) * 100 if self.total_pings > 0 else 0
        
        # Update display
        self.update_display()
    
    def update_display(self) -> None:
        """Update the statistics display"""
        self.update(
            f"Statistics:\n"
            f"Average Ping: {self.avg_ping:.1f} ms\n"
            f"Packet Loss: {self.packet_loss:.1f}%\n"
            f"Total Pings: {self.total_pings}"
        )
    
    def reset(self) -> None:
        """Reset all statistics"""
        self.total_pings = 0
        self.failed_pings = 0
        self.avg_ping = 0.0
        self.packet_loss = 0.0
        self.update_display()

class PingDisplay(Static):
    """Widget to display current ping results"""
    ping_result = reactive(0.00)
    is_running = reactive(False)
    target = reactive("1.1.1.1")

    def on_mount(self) -> None:
        self.update("Ready")
        self.console = self.app.query_one(ConsoleLog)
        self.stats = self.app.query_one(StatsDisplay)

    async def update_ping(self) -> None:
        """Asynchronously update ping results"""
        while self.is_running:
            try:
                timestamp = datetime.now().strftime('%H:%M:%S')
                result = await asyncio.to_thread(
                    lambda: ping(self.target, count=1)
                )
                
                if result.success():
                    self.ping_result = result.rtt_avg_ms
                    self.console.write(f"[{timestamp}] Reply from {self.target}: time={self.ping_result:.1f}ms")
                    self.stats.update_stats(self.ping_result, True)
                else:
                    self.console.write(f"[{timestamp}] Request timed out")
                    self.stats.update_stats(0, False)
                    
            except Exception as e:
                self.console.write(f"[{timestamp}] Error: {str(e)}")
                self.stats.update_stats(0, False)
                
            await asyncio.sleep(1)

    def watch_ping_result(self, ping_result: float) -> None:
        """Update display when ping_result changes"""
        if ping_result > 0:
            self.update(f"{ping_result:.1f} ms")
        else:
            self.update("No response")

    def set_target(self, new_target: str) -> None:
        """Set new ping target"""
        if new_target != self.target:
            self.target = new_target
            self.stats.reset()  # Reset stats for new target
            if self.is_running:
                self.console.write(f"\nChanged target to: {new_target}")

    def start(self) -> None:
        """Start ping updates"""
        if not self.is_running:
            self.is_running = True
            self.console.write(f"\nStarting ping monitoring to {self.target}...")
            self.stats.reset()  # Reset stats on start
            asyncio.create_task(self.update_ping())

    def stop(self) -> None:
        """Stop ping updates"""
        if self.is_running:
            self.is_running = False
            self.console.write("\nStopped ping monitoring")
            self.update("Ready")

class PingWindowMain(Static):
    """Main window with controls"""
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        ping_display = self.query_one(PingDisplay)
        
        if button_id == "start_test":
            self.start_ping()
        elif button_id == "stop_test":
            self.stop_ping()
        elif button_id == "speedtest":
            self.start_speedtest()
        elif button_id == "set_target":
            input_field = self.query_one(Input)
            new_target = input_field.value.strip()
            if new_target:
                ping_display.set_target(new_target)

    def start_ping(self) -> None:
        """Start ping monitoring"""
        ping_display = self.query_one(PingDisplay)
        self.add_class("started")
        ping_display.start()

    def stop_ping(self) -> None:
        """Stop ping monitoring"""
        ping_display = self.query_one(PingDisplay)
        self.remove_class("started")
        ping_display.stop()

    async def start_speedtest(self) -> None:
        """Start speedtest"""
        speedtest_display = self.query_one(SpeedTestDisplay)
        if not speedtest_display.is_testing:
            await speedtest_display.run_speedtest()

    def compose(self) -> ComposeResult:
        """Create child widgets"""
        with Grid():
            with Vertical():
                # First row: Input and Set button
                with Horizontal():
                    yield Input(placeholder="Enter IP or domain (e.g., google.com)", id="target_input")
                    yield Button("Set", id="set_target", variant="default")
                
                # Second row: Start/Stop buttons and Ping Display
                with Horizontal():
                    with Horizontal():
                        yield Button("Start (F5)", id="start_test", variant="success")
                        yield Button("Stop (F6)", id="stop_test", variant="error")
                    yield PingDisplay()
                
                # Third row: Speed Test button
                with Horizontal():
                    yield Button("Speed Test (F7)", id="speedtest", variant="primary")
                
                yield SpeedTestDisplay()
            yield StatsDisplay()

    async def start_speedtest(self) -> None:
        """Start speedtest"""
        speedtest_display = self.query_one(SpeedTestDisplay)
        if not speedtest_display.is_testing:
            await speedtest_display.run_speedtest()

    def compose(self) -> ComposeResult:
        """Create child widgets"""
        with Grid():
            with Vertical():
                with Horizontal():
                    yield Input(placeholder="Enter IP or domain (e.g., google.com)", id="target_input")
                    yield Button("Set", id="set_target", variant="default")
                with Horizontal():
                    yield Button("Start (F5)", id="start_test", variant="success")
                    yield Button("Stop (F6)", id="stop_test", variant="error")
                    yield PingDisplay()
                with Horizontal():
                    yield Button("Speed Test (F7)", id="speedtest", variant="primary")
                yield SpeedTestDisplay()
            yield StatsDisplay()

class PingMain(App):
    """Main application"""
    
    TITLE = "Ping Monitor"
    CSS_PATH = "main_style.tcss"
    BINDINGS = [
        ("f5", "start", "Start ping"),
        ("f6", "stop", "Stop ping"),
        ("f7", "speedtest", "Run speed test"),
        ("d", "toggle_dark", "Toggle dark mode"),
        ("c", "clear_logs", "Clear logs"),
        ("r", "reset_stats", "Reset stats"),
        ("ctrl+c", "quit", "Quit")
    ]

    def compose(self) -> ComposeResult:
        """Create app layout"""
        yield Header()
        yield ScrollableContainer(PingWindowMain())
        yield ConsoleLog()
        yield Footer()

    def action_speedtest(self) -> None:
        """Start speedtest (F7)"""
        asyncio.create_task(self.query_one(PingWindowMain).start_speedtest())

    def action_toggle_dark(self) -> None:
        """Toggle dark mode"""
        self.dark = not self.dark

    def action_clear_logs(self) -> None:
        """Clear the log"""
        self.query_one(ConsoleLog).clear()

    def action_reset_stats(self) -> None:
        """Reset statistics"""
        self.query_one(StatsDisplay).reset()

    def action_start(self) -> None:
        """Start ping monitoring (F5)"""
        self.query_one(PingWindowMain).start_ping()

    def action_stop(self) -> None:
        """Stop ping monitoring (F6)"""
        self.query_one(PingWindowMain).stop_ping()

if __name__ == "__main__":
    app = PingMain()
    app.run()