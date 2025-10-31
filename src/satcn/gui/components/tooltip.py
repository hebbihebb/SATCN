"""
Tooltip widget for CustomTkinter.

Provides hover tooltips for GUI elements.
"""


import customtkinter as ctk


class CTkToolTip:
    """
    Tooltip widget for CustomTkinter widgets.

    Shows a tooltip message when the user hovers over a widget.
    Based on the traditional tkinter tooltip pattern but styled for CustomTkinter.
    """

    def __init__(self, widget, message: str, delay: int = 500, follow_mouse: bool = True, **kwargs):
        """
        Create a tooltip for a widget.

        Args:
            widget: The widget to attach the tooltip to
            message: The tooltip message to display
            delay: Delay in milliseconds before showing tooltip
            follow_mouse: Whether tooltip follows mouse cursor
            **kwargs: Additional arguments for tooltip label styling
        """
        self.widget = widget
        self.message = message
        self.delay = delay
        self.follow_mouse = follow_mouse

        self.tooltip_window: ctk.CTkToplevel | None = None
        self.schedule_id: str | None = None

        # Default styling
        self.fg_color = kwargs.get("fg_color", "#2B2B2B")
        self.text_color = kwargs.get("text_color", "white")
        self.corner_radius = kwargs.get("corner_radius", 6)
        self.padding = kwargs.get("padding", 5)

        # Bind events
        self.widget.bind("<Enter>", self._on_enter, add="+")
        self.widget.bind("<Leave>", self._on_leave, add="+")
        self.widget.bind("<Motion>", self._on_motion, add="+")

    def _on_enter(self, event=None):
        """Handle mouse entering widget."""
        self._schedule_tooltip()

    def _on_leave(self, event=None):
        """Handle mouse leaving widget."""
        self._cancel_tooltip()
        self._hide_tooltip()

    def _on_motion(self, event=None):
        """Handle mouse motion over widget."""
        if self.tooltip_window and self.follow_mouse:
            self._update_position(event)

    def _schedule_tooltip(self):
        """Schedule tooltip to appear after delay."""
        self._cancel_tooltip()
        self.schedule_id = self.widget.after(self.delay, self._show_tooltip)

    def _cancel_tooltip(self):
        """Cancel scheduled tooltip."""
        if self.schedule_id:
            self.widget.after_cancel(self.schedule_id)
            self.schedule_id = None

    def _show_tooltip(self, event=None):
        """Show the tooltip window."""
        if self.tooltip_window:
            return  # Already showing

        # Create tooltip window
        self.tooltip_window = ctk.CTkToplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)  # Remove window decorations

        # Create label with message
        label = ctk.CTkLabel(
            self.tooltip_window,
            text=self.message,
            fg_color=self.fg_color,
            text_color=self.text_color,
            corner_radius=self.corner_radius,
            padx=self.padding,
            pady=self.padding,
        )
        label.pack()

        # Position tooltip
        self._update_position()

    def _update_position(self, event=None):
        """Update tooltip position near mouse cursor."""
        if not self.tooltip_window:
            return

        # Get mouse position
        x = self.widget.winfo_pointerx() + 15  # Offset from cursor
        y = self.widget.winfo_pointery() + 10

        # Update window position
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

    def _hide_tooltip(self):
        """Hide the tooltip window."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


def add_tooltip(widget, message: str, **kwargs):
    """
    Convenience function to add a tooltip to a widget.

    Args:
        widget: The widget to add tooltip to
        message: The tooltip message
        **kwargs: Additional tooltip styling options

    Returns:
        CTkToolTip instance
    """
    return CTkToolTip(widget, message, **kwargs)
