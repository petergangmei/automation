import pyautogui
import time

# Common configuration parameters
CONFIG = {
    'scroll_delay': 0.2,          # Delay between scroll actions
    'click_delay': 0.5,           # Delay after clicking
    'search_confidence': 0.8,     # Confidence level for image recognition
    'scroll_down_amount': -500,   # Amount to scroll down (negative)
    'scroll_up_amount': 400,      # Amount to scroll up (positive)
}

def locate_image(image_path, confidence=None, attempts=10, scroll_amount=100):
    """
    Locate an image on screen with multiple attempts.
    
    Args:
        image_path (str): Path to the image file
        confidence (float): Confidence level for image recognition (0-1)
        attempts (int): Number of attempts to find the image
        scroll_amount (int): Amount to scroll between attempts
        
    Returns:
        tuple: (x, y) center coordinates of found image, or None if not found
    """
    confidence = confidence or CONFIG['search_confidence']
    print(f"Looking for image: {image_path}...")
    
    for attempt in range(attempts):
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                print(f"Image found at: {location}")
                return pyautogui.center(location)
        except Exception as e:
            print(f"Search attempt {attempt+1}: {e}")
        
        # If image not found and we have more attempts, scroll and try again
        if attempt < attempts - 1:
            pyautogui.scroll(scroll_amount)
            time.sleep(CONFIG['scroll_delay'])
    
    print(f"Image not found: {image_path}")
    return None

def scroll_to_bottom(num_scrolls=20):
    """Scroll to the bottom of the page"""
    print("Scrolling to the bottom of the page...")
    for _ in range(num_scrolls):
        pyautogui.scroll(CONFIG['scroll_down_amount'])
        time.sleep(CONFIG['scroll_delay'])

def scroll_up(num_scrolls=5):
    """Scroll up by a specified amount"""
    print(f"Scrolling up {num_scrolls} times...")
    for _ in range(num_scrolls):
        pyautogui.scroll(CONFIG['scroll_up_amount'])
        time.sleep(CONFIG['scroll_delay'])

def select_and_copy_content(start_coords, end_selector=None, default_end_y=10):
    """
    Select content from start coordinates to end coordinates and copy
    
    Args:
        start_coords (tuple): (x, y) coordinates to start selection
        end_selector (dict): Configuration for finding the end selection point
        default_end_y (int): Default Y position if end_selector fails
    """
    if not start_coords:
        print("No starting position provided. Aborting.")
        return
    
    start_x, start_y = start_coords
    adjusted_y = start_y - 45  # Small adjustment to starting position
    
    # Start selection
    print(f"Starting selection at: ({start_x}, {adjusted_y})")
    pyautogui.click(start_x+200, adjusted_y)
    pyautogui.mouseDown(start_x+200, adjusted_y)
    time.sleep(CONFIG['click_delay'])
    
    # Scroll to the top while holding selection
    print("Scrolling to top while maintaining selection...")
    for _ in range(30):  # Adjust based on page length
        pyautogui.scroll(500)
        time.sleep(CONFIG['scroll_delay'])
    
    # Determine end position for selection
    end_x, end_y = start_x, default_end_y
    
    if end_selector and 'image_path' in end_selector:
        # Look for the end selection marker (e.g., search bar)
        end_coords = locate_image(
            end_selector['image_path'], 
            confidence=end_selector.get('confidence', CONFIG['search_confidence']),
            attempts=end_selector.get('attempts', 5)
        )
        
        if end_coords:
            end_x, end_y = end_coords
            # Apply offset if specified
            if 'offset_y' in end_selector:
                end_y += end_selector['offset_y']
                print(f"Using position with offset: ({end_x}, {end_y})")
    
    # Complete selection and copy
    pyautogui.moveTo(end_x+150, end_y-50, duration=1)
    pyautogui.mouseUp()
    
    # Copy selected text
    print("Copying selected text...")
    pyautogui.hotkey('ctrl', 'c')  # Use 'command', 'c' for Mac
    
    print("Selection and copy completed!")

def cover_to_json():
    print("Converting cover to JSON...")
    # Locate Chrome icon
    chrome_location = locate_image('./img/chrome.png')
    if not chrome_location:
        print("Chrome icon not found. Aborting.")
        return
    
    # Move to Chrome icon and adjust x-axis by 300
    chrome_x, chrome_y = chrome_location
    adjusted_x = chrome_x + 300

    # Click on the adjusted location
    pyautogui.click(adjusted_x, chrome_y)
    time.sleep(CONFIG['click_delay'])
    
    # Locate entry point for pasting
    entry_location = locate_image('./img/ask.png')
    if not entry_location:
        print("Entry point not found. Aborting.")
        return
    
    # Move to entry location and adjust y-axis by -50 (move up)
    entry_x, entry_y = entry_location
    adjusted_entry_y = entry_y - 10
    pyautogui.moveTo(entry_x, adjusted_entry_y)

    # Click and paste
    pyautogui.click()
    time.sleep(CONFIG['click_delay'])
    pyautogui.hotkey('ctrl', 'v')  # Use 'command', 'v' for Mac
    
    print("Copy to sheet completed!")

    send_location = locate_image('./img/send.png')
    if not send_location:
        print("Send button not found. Aborting. Wait for 5 seconds and check again ")
        time.sleep(5)
        cover_to_json()
        return
    
    send_x, send_y = send_location
    pyautogui.moveTo(send_x, send_y)
    pyautogui.click()


def scroll_select_and_copy(
    target_image_path='./img/rnr.png', 
    searchbar_image_path='./img/searchbar.png', 
    preparation_delay=3
):
    """
    Main function to scroll, select content between two points, and copy.
    
    Args:
        target_image_path (str): Path to the target image that marks start of selection
        searchbar_image_path (str): Path to the search bar image
        preparation_delay (int): Initial delay to switch to browser
    """
    # Give time to switch to the browser window
    print(f"Switching to browser in {preparation_delay} seconds...")
    time.sleep(preparation_delay)
    
    # Scroll to bottom and then up slightly
    scroll_to_bottom()
    scroll_up(5)
    
    # Find the target image for starting selection
    start_coords = locate_image(target_image_path)
    if not start_coords:
        print("Target image could not be found. Aborting.")
        return
    
    # Configure the end selection point
    end_selector = {
        'image_path': searchbar_image_path,
        'confidence': CONFIG['search_confidence'],
        'attempts': 5,
        'offset_y': 140  # 130px below search bar
    }
    
    # Perform the selection and copy
    select_and_copy_content(start_coords, end_selector)
    
    # Operation completed
    print("Operation completed successfully!")

    cover_to_json()

if __name__ == "__main__":
    # Run the function
    print("Starting scroll, select, and copy operation...")
    scroll_select_and_copy()