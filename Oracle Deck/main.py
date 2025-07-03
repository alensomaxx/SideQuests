import random

def create_deck():
    """
    Initializes a deck of 21 cards.
    Cards are represented as strings like "Card 1", "Card 2", etc.
    """
    return [f"Card {i}" for i in range(1, 22)]

def display_piles(piles):
    """
    Prints the three piles clearly for the player to see.
    """
    for i, pile in enumerate(piles):
        print(f"--- Pile {i+1} ---")
        # Print cards in an easy-to-read format, e.g., on separate lines or with good spacing
        print(", ".join(pile))
    print("-" * 20)

def reassemble_deck(piles, chosen_pile_index):
    """
    Reassembles the deck based on the player's choice,
    ensuring the chosen pile is always placed in the middle.

    Args:
        piles (list of lists): The three current piles of cards.
        chosen_pile_index (int): The 0-based index of the pile chosen by the player.

    Returns:
        list: The newly reassembled deck of 21 cards.
    """
    # The logic here is crucial for the trick to work.
    # The chosen pile always goes in the middle.
    if chosen_pile_index == 0:  # Player chose Pile 1 (index 0)
        # New order: Pile 2 + Pile 1 + Pile 3
        return piles[1] + piles[0] + piles[2]
    elif chosen_pile_index == 1: # Player chose Pile 2 (index 1)
        # New order: Pile 1 + Pile 2 + Pile 3 (Pile 2 is already in the middle)
        return piles[0] + piles[1] + piles[2]
    else: # Player chose Pile 3 (index 2)
        # New order: Pile 1 + Pile 3 + Pile 2
        return piles[0] + piles[2] + piles[1]

def play_game(debug_mode=False):
    """
    Main function to run the 21-card mind game.

    Args:
        debug_mode (bool): If True, reveals the chosen card's position for debugging.
    """
    deck = create_deck()
    random.shuffle(deck) # Initial shuffle for randomness

    print("Welcome to The Oracle Deck!")
    print("Mentally choose one card from the following. Don't tell me what it is!")
    print("-" * 50)
    print(", ".join(deck))
    print("-" * 50)

    # In a real game, the user would remember a card.
    # For debugging, we can simulate them picking one, or have them tell us.
    if debug_mode:
        print("\n--- DEBUG MODE ---")
        chosen_card_str = input("DEBUG: Which card will you 'mentally' choose? (e.g., 'Card 5'): ")
        while chosen_card_str not in deck:
            chosen_card_str = input(f"DEBUG: '{chosen_card_str}' not in deck. Please enter a valid card (e.g., 'Card 5'): ")
        print(f"DEBUG: You 'chose' {chosen_card_str}. We will track this.\n")
    else:
        input("Press Enter when you have chosen your card...")

    current_deck = deck

    for round_num in range(1, 4): # The trick requires exactly 3 rounds
        print(f"\n--- Round {round_num} ---")
        
        # Divide the current deck into three piles of 7 cards each
        piles = [current_deck[i:i+7] for i in range(0, 21, 7)]
        display_piles(piles)

        while True:
            try:
                choice = int(input("Which pile contains your card? (Enter 1, 2, or 3): "))
                if 1 <= choice <= 3:
                    break
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        # Adjust choice to 0-based index for list access
        chosen_pile_idx = choice - 1
        
        # Reassemble the deck using the helper function
        current_deck = reassemble_deck(piles, chosen_pile_idx)

        if debug_mode:
            try:
                # Find the position of the chosen card in the reassembled deck
                current_position = current_deck.index(chosen_card_str)
                print(f"DEBUG: After round {round_num}, '{chosen_card_str}' is at index {current_position} (position {current_position + 1}).")
            except ValueError:
                print(f"DEBUG: Error: '{chosen_card_str}' not found in the deck after reassembly. (This shouldn't happen!)")


    print("\n--- The Grand Reveal! ---")
    print("After all that mystical shuffling, your chosen card must be...")
    
    # The magic moment: the 11th card (index 10) is always the chosen one!
    predicted_card = current_deck[10] 
    print(f"Is it... {predicted_card}?! ✨")
    print("\nThanks for playing The Oracle Deck!")


if __name__ == "__main__":
    # To run in debug mode, change play_game() to play_game(debug_mode=True)
    # This will ask you to "mentally choose" a card and then track its position.
    play_game(debug_mode=False)