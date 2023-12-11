import pygame

from Pieces import Pieces


class PromotionPopup:
    """
    Graphical popup for selecting a piece during pawn promotion.

    Attributes:
    - screen: The Pygame screen where the popup is displayed.
    - options: A list of available promotion pieces (excluding pawn and king).
    - buttons: A list of button surfaces representing the promotion piece options.
    - font: The Pygame font used for rendering text.
    - title: The rendered title text for the popup.
    """

    def __init__(self, screen, pieces):
        """
        Initialize the PromotionPopup.

        Parameters:
        - screen: The Pygame screen where the popup is displayed.
        - pieces: A list of available promotion pieces (excluding pawn and king).
        """

        self.screen = screen
        self.options = [piece for piece in pieces if piece.get_piece_type() != Pieces.PAWN and
                        piece.get_piece_type() != Pieces.KING]
        self.buttons = []
        self.font = pygame.font.Font(None, 45)
        self.title = self.font.render("Pick a promotion piece:", True, (255, 255, 255))

        for i, piece in enumerate(self.options):
            button_surface = piece.get_icon()
            self.buttons.append(button_surface)

    def draw(self):
        """
        Draw the promotion popup on the screen.
        """

        pygame.draw.rect(self.screen, (0, 0, 0), (200, 300, 400, 200))
        title_rect = self.title.get_rect(center=(400, 330))
        self.screen.blit(self.title, title_rect.topleft)

        for i, button_surface in enumerate(self.buttons):
            self.screen.blit(button_surface, (200 + 100 * i, 350))

    def handle_click(self, click_position):
        """
        Handle a mouse click within the popup area.

        Parameters:
        - click_position: The position of the mouse click.

        Returns:
        The type of the selected promotion piece if a button was clicked, otherwise, None.
        """
        for i, button_surface in enumerate(self.buttons):
            if button_surface.get_rect(topleft=(200 + 100 * i, 350)).collidepoint(click_position):
                return self.options[i]
        return None
