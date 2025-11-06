from finsight.utils.ui import UI


class Logger:
    """Logger that uses the new interactive UI system."""
    
    def __init__(self):
        self.ui = UI()
        self.log = []
        # Subscribers are callables that will be invoked with new log messages.
        # Callables must be thread-safe; we use loop.call_soon_threadsafe from the WebSocket handler.
        self._subscribers = []

    def _log(self, msg: str):
        """Print immediately and keep in log."""
        print(msg, flush=True)
        self.log.append(msg)
        # Notify subscribers
        for sub in list(self._subscribers):
            try:
                sub(msg)
            except Exception:
                # Ignore subscriber errors to not break logging
                continue

    def log_header(self, msg: str):
        self.ui.print_header(msg)
    
    def log_user_query(self, query: str):
        self.ui.print_user_query(query)

    def log_task_list(self, tasks):
        self.ui.print_task_list(tasks)

    def log_task_start(self, task_desc: str):
        self.ui.print_task_start(task_desc)

    def log_task_done(self, task_desc: str):
        self.ui.print_task_done(task_desc)
        
    def log_tool_run(self, params: dict, result: dict):
        self.ui.print_tool_params(str(params))
        self.ui.print_tool_run(str(result))

    def log_risky(self, tool: str, input_str: str):
        self.ui.print_warning(f"Risky action {tool}({input_str}) — auto-confirmed")

    def log_summary(self, summary: str):
        self.ui.print_answer(summary)
    
    def progress(self, message: str, success_message: str = ""):
        """Return a progress context manager for showing loading states."""
        return self.ui.progress(message, success_message)

    # Subscription API for external listeners (e.g., WebSocket stream)
    def subscribe(self, callback):
        """Register a callable to receive new log messages.

        The callback will be called with a single string argument (the log message).
        Return the callback so the caller can pass it to unsubscribe.
        """
        self._subscribers.append(callback)
        return callback

    def unsubscribe(self, callback):
        try:
            self._subscribers.remove(callback)
        except ValueError:
            pass
