import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QRadioButton, QButtonGroup, QMessageBox,
    QGridLayout, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap, QIcon, QColor

# --- Constants for Game Logic ---
NUM_CARDS = 21
NUM_PILES = 3
NUM_ROUNDS = 3
# The magic index for the final card. For 21 cards, it's the 11th card (index 10).
# This is calculated as (NUM_CARDS - 1) // 2.
FINAL_CARD_INDEX = (NUM_CARDS - 1) // 2


# --- Core Game Logic ---

def create_deck():
    """Initializes a deck of cards."""
    return [f"Card {i}" for i in range(1, NUM_CARDS + 1)]

def deal_into_piles(deck):
    """
    Deals a deck of cards into a specified number of piles.

    Args:
        deck (list): The list of cards to deal.

    Returns:
        list: A list of lists, where each inner list represents a pile.
    """
    piles = [[] for _ in range(NUM_PILES)]
    for index, card in enumerate(deck):
        piles[index % NUM_PILES].append(card)
    return piles

def reassemble_deck(piles, chosen_pile_index):
    """
    Reassembles the deck, placing the chosen pile in the middle.
    This is the core mechanism of the card trick.

    Args:
        piles (list): The list of card piles.
        chosen_pile_index (int): The index of the pile the user selected.

    Returns:
        list: The new, reassembled deck.
    """
    # Remove the chosen pile from its current position.
    chosen_pile = piles.pop(chosen_pile_index)
    # Re-insert the chosen pile into the middle of the list of piles.
    piles.insert(1, chosen_pile)
    # Flatten the list of piles back into a single deck.
    return [card for pile in piles for card in pile]


# --- Custom Widgets for Better UX ---

class CardLabel(QLabel):
    """A custom QLabel to represent a single card, with hover effects."""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setObjectName("card_label_base")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Add a subtle drop shadow for depth.
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(5)
        shadow.setXOffset(2)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(shadow)
        self.is_pile_card = False

    def set_as_pile_card(self):
        """Configures the label to be displayed within a pile."""
        self.is_pile_card = True
        self.setFixedSize(100, 50)
        self.setObjectName("pile_card_label")

    def enterEvent(self, event):
        """Handles mouse hover event to trigger a style change."""
        if not self.is_pile_card:
            # Set a dynamic property 'hover' to True for QSS to catch.
            self.setProperty("hover", True)
            # Re-polish the widget to apply the updated style.
            self.style().polish(self)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handles mouse leave event to revert the style change."""
        if not self.is_pile_card:
            # Set the dynamic property 'hover' to False.
            self.setProperty("hover", False)
            # Re-polish the widget to apply the updated style.
            self.style().polish(self)
        super().leaveEvent(event)


class PileWidget(QWidget):
    """A composite widget representing a pile of cards and its radio button."""
    def __init__(self, pile_index, parent=None):
        super().__init__(parent)
        # Use a dynamic property for styling when selected.
        self.setProperty("checked", False)
        self.setObjectName("PileContainer")
        self.setContentsMargins(15, 15, 15, 15)

        # Main layout for the pile.
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.layout.setSpacing(5)

        # Title label for the pile.
        self.title_label = QLabel(f"--- Pile {pile_index + 1} ---")
        self.title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_label)

        # A dedicated layout to hold the card labels.
        self.card_vbox_layout = QVBoxLayout()
        self.card_vbox_layout.setSpacing(5)
        self.layout.addLayout(self.card_vbox_layout)

        self.layout.addStretch()  # Pushes the radio button to the bottom.

        # Radio button for user selection.
        self.radio_button = QRadioButton(f"Pile {pile_index + 1}")
        self.radio_button.setFont(QFont("Segoe UI", 14))
        self.layout.addWidget(self.radio_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def update_cards(self, cards):
        """Clears and repopulates the pile with new cards."""
        # Clear existing cards to prevent duplication.
        while self.card_vbox_layout.count():
            item = self.card_vbox_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()

        # Add new card labels to the pile.
        for card_name in cards:
            card_label = CardLabel(card_name)
            card_label.set_as_pile_card()
            self.card_vbox_layout.addWidget(card_label)


# --- Main Application Window ---

class OracleDeckApp(QMainWindow):
    """The main window for The Oracle Deck application."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("The Oracle Deck")
        self.setGeometry(100, 100, 1000, 750)
        self.setMinimumSize(900, 650)
        self.setWindowIcon(QIcon('magic_hat.png'))

        # Game state variables
        self.deck = []
        self.current_deck = []
        self.current_piles = []
        self.round_num = 0

        # Central widget and layout setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Stacked widget to manage different screens (pages)
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        # Create all UI pages
        self.create_welcome_screen()
        self.create_card_selection_screen()
        self.create_game_screen()
        self.create_reveal_screen()

        # Apply the application-wide stylesheet
        self.setStyleSheet(self.get_stylesheet())
        self.stacked_widget.setCurrentIndex(0) # Start at the welcome screen

    def get_stylesheet(self):
        """Returns the QSS stylesheet for the entire application."""
        return """
            QMainWindow {
                background-color: #2E3440; /* Nord Dark Polar Night */
                font-family: 'Segoe UI', 'Roboto', sans-serif;
            }
            QLabel { color: #ECEFF4; }
            QLabel#RoundLabel {
                font-size: 26px;
                font-weight: bold;
                color: #A3BE8C; /* Nord Green */
                padding: 15px 0 10px 0;
            }
            QLabel#InstructionLabel {
                font-size: 20px;
                font-weight: bold;
                color: #BF616A; /* Nord Red */
                margin-bottom: 15px;
            }
            QLabel#PredictedCardLabel {
                font-size: 64px;
                font-weight: bold;
                color: #EBCB8B; /* Nord Orange/Yellow */
                min-height: 120px;
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4C566A, stop:1 #3B4252);
                border-radius: 15px;
                padding: 20px;
            }
            QPushButton {
                background-color: #5E81AC; /* Nord Blue */
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #81A1C1; }
            QPushButton:pressed { background-color: #4C566A; }
            
            QRadioButton {
                color: #D8DEE9;
                font-size: 15px;
                spacing: 15px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border-radius: 10px;
                border: 2px solid #8FBCBB; /* Nord Aqua */
                background-color: #4C566A;
            }
            QRadioButton::indicator:hover { border: 2px solid #88C0D0; }
            QRadioButton::indicator:checked { background-color: #8FBCBB; }

            QWidget#CardDisplayArea {
                background-color: #3B4252;
                border-radius: 15px;
                padding: 20px;
            }
            
            /* Style for selection cards. The [hover] property is set in CardLabel code. */
            QLabel#card_label_base {
                background-color: #4C566A;
                color: #ECEFF4;
                border: 1px solid #D8DEE9;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                font-weight: 500;
            }
            QLabel#card_label_base[hover="true"] {
                background-color: #5E81AC;
                border: 2px solid #88C0D0;
            }
            
            /* Style for pile containers. The [checked] property is set in the code. */
            QWidget#PileContainer {
                background-color: #3B4252;
                border-radius: 10px;
                padding: 10px;
                margin: 8px;
                border: 2px solid transparent;
            }
            QWidget#PileContainer[checked="true"] {
                border: 2px solid #8FBCBB; /* Nord Aqua border for selected pile */
                background-color: #434C5E;
            }
            
            /* Style for cards inside piles. */
            QLabel#pile_card_label {
                background-color: #4C566A;
                color: #D8DEE9;
                border: 1px solid #4C566A;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 13px;
                font-weight: normal;
            }
            
            /* Welcome Screen specific styles */
            QWidget#WelcomePage {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2E3440, stop:1 #3B4252);
            }
            QLabel#WelcomeTitle {
                font-size: 48px;
                font-weight: bold;
                color: #D8DEE9;
            }
            QLabel#WelcomeSubtitle {
                font-size: 22px;
                color: #E5E9F0;
                margin-bottom: 30px;
            }
        """

    def create_welcome_screen(self):
        """Builds the UI for the welcome page."""
        welcome_page = QWidget()
        welcome_page.setObjectName("WelcomePage")
        layout = QVBoxLayout(welcome_page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        title = QLabel("Welcome to The Oracle Deck!")
        title.setObjectName("WelcomeTitle")
        subtitle = QLabel("Prepare to have your mind read!")
        subtitle.setObjectName("WelcomeSubtitle")
        
        try:
            pixmap = QPixmap('magic_hat.png')
            if pixmap.isNull(): raise FileNotFoundError
            image_label = QLabel()
            image_label.setPixmap(pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        except (FileNotFoundError, Exception) as e:
            print(f"Warning: Could not load 'magic_hat.png'. {e}. Using fallback emoji.")
            image_label = QLabel("🔮")
            image_label.setFont(QFont("Segoe UI", 80))
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        start_button = QPushButton("Start Game")
        start_button.clicked.connect(self.start_game)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(image_label)
        layout.addWidget(start_button)
        self.stacked_widget.addWidget(welcome_page)

    def create_card_selection_screen(self):
        """Builds the UI for the initial card selection page."""
        self.card_selection_page = QWidget()
        layout = QVBoxLayout(self.card_selection_page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(30, 30, 30, 30)

        instruction = QLabel("Mentally choose one card. Don't tell me what it is!")
        instruction.setObjectName("InstructionLabel")
        instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instruction)

        # The grid will hold the 21 cards.
        self.card_display_grid = QGridLayout()
        self.card_display_grid.setSpacing(15)
        # Set stretch factor for each column to ensure they are evenly spaced.
        for i in range(7):
            self.card_display_grid.setColumnStretch(i, 1)

        card_area = QWidget()
        card_area.setObjectName("CardDisplayArea")
        card_area.setLayout(self.card_display_grid)
        card_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(card_area, stretch=1, alignment=Qt.AlignmentFlag.AlignCenter)

        self.chosen_button = QPushButton("I've Chosen My Card")
        self.chosen_button.clicked.connect(self.start_round)
        layout.addWidget(self.chosen_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.stacked_widget.addWidget(self.card_selection_page)

    def create_game_screen(self):
        """Builds the UI for the main game page where piles are shown."""
        self.game_page = QWidget()
        layout = QVBoxLayout(self.game_page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(30, 20, 30, 30)

        self.round_label = QLabel()
        self.round_label.setObjectName("RoundLabel")
        self.round_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.round_label)

        instruction = QLabel("Which pile contains your card?")
        instruction.setObjectName("InstructionLabel")
        instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instruction)

        # Horizontal layout to hold the three pile widgets.
        self.piles_container_layout = QHBoxLayout()
        self.piles_container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(self.piles_container_layout)

        # Button group to manage radio button exclusivity.
        self.radio_button_group = QButtonGroup(self)
        self.radio_button_group.idClicked.connect(self.update_pile_highlights)

        self.pile_widgets_list = []
        for i in range(NUM_PILES):
            pile_widget = PileWidget(i)
            self.pile_widgets_list.append(pile_widget)
            self.piles_container_layout.addWidget(pile_widget)
            self.radio_button_group.addButton(pile_widget.radio_button, i)
            # This connection allows us to style the *entire* PileWidget when its radio button is checked.
            pile_widget.radio_button.toggled.connect(
                lambda checked, pw=pile_widget: self.on_pile_toggled(checked, pw)
            )

        layout.addStretch(1) # Pushes confirm button to the bottom.
        self.confirm_button = QPushButton("Confirm Choice")
        self.confirm_button.clicked.connect(self.process_choice)
        layout.addWidget(self.confirm_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.stacked_widget.addWidget(self.game_page)

    def create_reveal_screen(self):
        """Builds the UI for the final card reveal page."""
        self.reveal_page = QWidget()
        layout = QVBoxLayout(self.reveal_page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)

        title = QLabel("--- The Grand Reveal! ---")
        title.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
        text = QLabel("After that mystical shuffling, your chosen card must be...")
        text.setFont(QFont("Segoe UI", 24))
        self.predicted_card_label = QLabel()
        self.predicted_card_label.setObjectName("PredictedCardLabel")
        
        play_again_button = QPushButton("Play Again")
        play_again_button.clicked.connect(self.reset_game)

        layout.addWidget(title)
        layout.addWidget(text)
        layout.addWidget(self.predicted_card_label)
        layout.addSpacing(50)
        layout.addWidget(play_again_button)
        self.stacked_widget.addWidget(self.reveal_page)

    def start_game(self):
        """Initializes game state and displays the card selection screen."""
        self.deck = create_deck()
        random.shuffle(self.deck)
        self.current_deck = list(self.deck)
        self.round_num = 0

        self.clear_layout(self.card_display_grid)
        num_cols = 7
        for i, card_name in enumerate(self.current_deck):
            card_label = CardLabel(card_name)
            self.card_display_grid.addWidget(card_label, i // num_cols, i % num_cols)
        
        self.stacked_widget.setCurrentIndex(1) # Switch to card selection screen

    def start_round(self):
        """Starts a new round: deals cards, updates UI, and switches to game screen."""
        self.round_num += 1
        self.round_label.setText(f"Round {self.round_num} of {NUM_ROUNDS}")

        # Reset radio buttons and visual highlights for the new round.
        self.radio_button_group.setExclusive(False) # Allow all to be unchecked
        for pile_widget in self.pile_widgets_list:
            pile_widget.radio_button.setChecked(False)
        self.radio_button_group.setExclusive(True) # Re-enable exclusive behavior

        self.current_piles = deal_into_piles(self.current_deck)
        self.display_piles_gui()
        self.stacked_widget.setCurrentIndex(2) # Switch to game screen

    def display_piles_gui(self):
        """Updates each PileWidget with the cards for the current round."""
        for i, pile_cards in enumerate(self.current_piles):
            # Delegate the work to the PileWidget's own update method.
            self.pile_widgets_list[i].update_cards(pile_cards)

    def on_pile_toggled(self, checked, pile_widget):
        """Sets a dynamic property on the pile widget for QSS styling."""
        pile_widget.setProperty("checked", checked)
        pile_widget.style().polish(pile_widget)
        
    def update_pile_highlights(self, checked_id):
        """Ensures all pile highlights are correct when a radio button is clicked."""
        for i, pile_widget in enumerate(self.pile_widgets_list):
            is_checked = (i == checked_id)
            if pile_widget.property("checked") != is_checked:
                pile_widget.setProperty("checked", is_checked)
                pile_widget.style().polish(pile_widget)

    def process_choice(self):
        """Processes the user's pile choice and advances the game."""
        chosen_pile_id = self.radio_button_group.checkedId()
        
        if chosen_pile_id == -1: # No radio button was selected
            QMessageBox.warning(self, "Selection Required", "Please select the pile containing your card.")
            return

        self.current_deck = reassemble_deck(self.current_piles, chosen_pile_id)

        if self.round_num < NUM_ROUNDS:
            self.start_round()
        else:
            self.reveal_card()

    def reveal_card(self):
        """Reveals the predicted card to the user."""
        predicted_card = self.current_deck[FINAL_CARD_INDEX]
        self.predicted_card_label.setText(f"{predicted_card} ✨")
        self.stacked_widget.setCurrentIndex(3) # Switch to reveal screen

    def reset_game(self):
        """Resets the game state and returns to the welcome screen."""
        self.round_num = 0
        self.deck = []
        self.current_deck = []
        self.current_piles = []
        self.stacked_widget.setCurrentIndex(0) # Go back to welcome screen

    def clear_layout(self, layout):
        """Recursively removes all widgets from a given layout."""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OracleDeckApp()
    window.show()
    sys.exit(app.exec())