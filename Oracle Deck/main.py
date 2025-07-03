import random

def create_deck():
    """
    Initializes a deck of 21 cards.
    Cards can be represented as numbers, strings, etc.
    """
    return [f"Card {i}" for i in range(1, 22)] # Example: ['Card 1', ..., 'Card 21']

def display_piles(piles):
    """
    Prints the three piles clearly for the player to see.
    """
    for i, pile in enumerate(piles):
        print(f"--- Pile {i+1} ---")
        print(", ".join(pile))
    print("-" * 20)

def reassemble_deck(piles, chosen_pile_index):
    """
    Reassembles the deck based on the player's choice.
    The chosen pile is always placed in the middle.
    """
    chosen_pile = piles[chosen_pile_index]
    other_piles = [p for i, p in enumerate(piles) if i != chosen_pile_index]

    # The trick: place the chosen pile in the middle
    # There are two 'other' piles. We need to decide which one goes first.
    # A simple way: concatenate them such that the chosen pile is always central.
    # For example, if chosen_pile_index is 0 (Pile 1), it goes between other_piles[0] and other_piles[1]
    # If chosen_pile_index is 1 (Pile 2), it stays between other_piles[0] and other_piles[1]
    # If chosen_pile_index is 2 (Pile 3), it goes between other_piles[0] and other_piles[1]

    # Let's correctly implement the reassembly as per the trick's requirement:
    # If chosen pile is P1, new deck = P2 + P1 + P3 (assuming P2, P3 are the others)
    # If chosen pile is P2, new deck = P1 + P2 + P3 (assuming P1, P3 are the others)
    # If chosen pile is P3, new deck = P1 + P3 + P2 (assuming P1, P2 are the others)

    if chosen_pile_index == 0:  # Player chose Pile 1
        return other_piles[0] + chosen_pile + other_piles[1]
    elif chosen_pile_index == 1: # Player chose Pile 2
        return other_piles[0] + chosen_pile + other_piles[1]
    else: # Player chose Pile 3
        return other_piles[0] + chosen_pile + other_piles[1]


def play_game():
    """
    Main function to run the 21-card mind game.
    """
    deck = create_deck()
    random.shuffle(deck) # Initial shuffle for randomness

    print("Welcome to The Oracle Deck!")
    print("Mentally choose one card from the following. Don't tell me what it is!")
    print("-" * 50)
    print(", ".join(deck))
    print("-" * 50)
    input("Press Enter when you have chosen your card...")

    current_deck = deck

    for round_num in range(1, 4):
        print(f"\n--- Round {round_num} ---")
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
        
        # Reassemble the deck based on the chosen pile
        # This part is critical for the trick to work.
        # The chosen pile must be placed in the *middle* position.
        
        if chosen_pile_idx == 0: # If player chose Pile 1 (index 0)
            current_deck = piles[1] + piles[0] + piles[2] # P2 + P1 + P3
        elif chosen_pile_idx == 1: # If player chose Pile 2 (index 1)
            current_deck = piles[0] + piles[1] + piles[2] # P1 + P2 + P3
        else: # If player chose Pile 3 (index 2)
            current_deck = piles[0] + piles[2] + piles[1] # P1 + P3 + P2

    print("\n--- The Grand Reveal! ---")
    print("After all that shuffling, your chosen card must be...")
    
    # The magic moment: the 11th card (index 10) is always the chosen one!
    predicted_card = current_deck[10] 
    print(f"Is it... {predicted_card}?! ✨")
    print("\nThanks for playing Oracle Deck!")


if __name__ == "__main__":
    play_game()