import logging
import threading
import time
from time import sleep

from textual import on
from textual.widgets import TextArea

from pylightlib.msc.Singleton import Singleton  # type: ignore

from model.config import Config  # type: ignore
from model.notes import Notes    # type: ignore
from view.main_tabs import MainTabs  # type: ignore


class NotesController(metaclass=Singleton):
    """
    Controller for the Notes tab in the application.

    This class handles the interaction between the Notes model and the UI.
    It implements a throttle and debounce mechanism to optimize performance
    when the user types in the TextArea.

    Attributes:
        config: The configuration object.
        notes_model: The notes model object.
        main_tabs: The main tabs object.
        throttle_interval: Time interval for the throttle mechanism.
        debounce_interval: Time interval for the debounce mechanism.
        last_throttle_call: Timestamp of the last throttle call.
        latest_text: The latest text entered in the TextArea.
        throttle_lock: A threading lock for thread-safe operations.
        debounce_timer: A timer for the debounce mechanism.
    """
    config: Config
    notes_model: Notes
    main_tabs: MainTabs
    throttle_interval: float = 5.0
    debounce_interval: float = 5.0
    last_throttle_call: float = 0.0
    latest_text: str = ''
    throttle_lock = threading.Lock()
    debounce_timer: threading.Timer | None = None


    def __init__(self, config: Config, notes_model: Notes, main_tabs: MainTabs):
        """
        Initializes the NotesController.

        Args:
            config: The configuration object.
            notes_model: The notes model object.
            main_tabs: The main tabs object.
        """
        self.config = config
        self.notes_model = notes_model
        self.main_tabs = main_tabs

        self.setup_textarea()

    def setup_textarea(self) -> None:
        """
        Sets the event handler for the TextArea in the Notes tab.
        """
        notes_tab = self.main_tabs.notes_tab
        notes_tab.text_area_changed_action = self.text_area_changed_action


    def text_area_changed_action(self, text: str) -> None:

        now = time.time()
        self.latest_text = text

        # --- THROTTLE: alle 5 Sekunden ---
        with self.throttle_lock:
            if now - self.last_throttle_call >= self.throttle_interval:
                self.last_throttle_call = now
                threading.Thread(target=self._throttle_action, args=(text,)).start()

        # --- DEBOUNCE: letzte Änderung nach 5 Sekunden Inaktivität ---
        if self.debounce_timer:
            self.debounce_timer.cancel()
        self.debounce_timer = threading.Timer(self.debounce_interval, self._debounce_action)
        self.debounce_timer.start()

    def _throttle_action(self, text: str):
        logging.info(f"⏱ THROTTLE (Zwischenspeichern): {text}")
        # Beispiel: self.notes_model.save_draft(text)

    def _debounce_action(self):
        logging.info(f"🛑 DEBOUNCE (Final speichern): {self.latest_text}")
        # Beispiel: self.notes_model.save_final(self._latest_text)

