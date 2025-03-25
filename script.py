import pyautogui
import time
import platform
import pyperclip

# Detect operating system
IS_MAC = platform.system() == 'Darwin'

# Common configuration parameters
CONFIG = {
    'scroll_delay': 0.2,          # Delay between scroll actions
    'click_delay': 0.5,           # Delay after clicking
    'search_confidence': 0.8,     # Confidence level for image recognition
    'scroll_down_amount': -500,   # Amount to scroll down (negative)
    'scroll_up_amount': 400,      # Amount to scroll up (positive)
}

# Default text to paste before the copied content
DEFAULT_TEXT = """Convert the following raw text into a structured JSON object with the following rules:
The JSON should have this structure:
{
  "book": "Name of the book",
  "slug:""name-of-the-book",
  "chapter": ChapterNumber,
  "language": "ruanglat",
  "content": [
    { "heading": "Heading text" },
    { "1", "Verse 1 text here." },
    { "2", "Verse 2 text here." },
    ...
  ]
}
"book" and "chapter" should be extracted or set manually if not available.
"language" is always "ruanglat".
In the "content" array:
If a line starts with a number and space (e.g. 1 Lorem ipsum), treat it as a verse:
Extract the number as "verse" and the rest as "text".
If a line does not start with a number, treat it as a heading:
Add it as { "heading": "Your Heading Here" }.
Keep all lines in original order, alternating between headings and verses as they appear.
"""

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
    # print(f"Looking for image: {image_path}...")
    
    for attempt in range(attempts):
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                # print(f"Image found at: {location}")
                return pyautogui.center(location)
        except Exception as e:
            print('----')
            # print(f"Search attempt {attempt+1}: {e}")
        
        # If image not found and we have more attempts, scroll and try again
        if attempt < attempts - 1:
            pyautogui.scroll(scroll_amount)
            time.sleep(CONFIG['scroll_delay'])
    
    # print(f"Image not found: {image_path}")
    return None

def scroll_to_bottom(num_scrolls=20):
    """Scroll to the bottom of the page"""
    print("Scrolling to the bottom of the page...")
    for _ in range(num_scrolls):
        pyautogui.scroll(CONFIG['scroll_down_amount'])
        time.sleep(CONFIG['scroll_delay'])

def scroll_up_until_found(target_image_path, max_scrolls=30, scroll_amount=400):
    """
    Scroll up while checking for target image after each scroll
    
    Args:
        target_image_path (str): Path to the image to look for
        max_scrolls (int): Maximum number of scrolls to attempt
        scroll_amount (int): Amount to scroll up each time (positive value)
        
    Returns:
        tuple: (x, y) coordinates of found image, or None if not found after max_scrolls
    """
    print(f"Scrolling up while looking for {target_image_path}...")
    
    for scroll_count in range(max_scrolls):
        # Check for image first
        target_coords = locate_image(
            target_image_path, 
            confidence=CONFIG['search_confidence'],
            attempts=1,  # Just one attempt per scroll
            scroll_amount=0  # Don't scroll inside locate_image
        )
        
        if target_coords:
            print(f"Target image found after {scroll_count} scrolls")
            return target_coords
        
        # Not found, scroll up and try again
        print(f"Scroll up attempt {scroll_count + 1}/{max_scrolls}")
        pyautogui.scroll(scroll_amount)  # Positive for up
        time.sleep(CONFIG['scroll_delay'])
    
    print(f"Target image not found after {max_scrolls} scroll attempts")
    return None

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
    
    # Move to initial position
    print(f"Moving to initial position: ({start_x}, {start_y})")
    pyautogui.moveTo(start_x, start_y)
    
    # Move relative to that position for selection start
    print("Moving to adjusted position for selection...")
    pyautogui.moveRel(250, -48)
    adjusted_position = pyautogui.position()
    print(f"Adjusted position: {adjusted_position}")
    
    # Start selection
    pyautogui.click()
    pyautogui.mouseDown()
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
    
    # Move to the end coordinates
    pyautogui.moveTo(end_x, end_y)
    
    # Move relative to that position for selection end
    print("Moving to end selection position...")
    pyautogui.moveRel(-250, -10, duration=1)
    end_position = pyautogui.position()
    print(f"End selection position: {end_position}")
    
    # Complete selection
    pyautogui.mouseUp()
    
    # Copy selected text
    print("Copying selected text...")
    # Use the appropriate hotkey based on OS
    if IS_MAC:
        pyautogui.hotkey('command', 'c')
    else:
        pyautogui.hotkey('ctrl', 'c')
    
    print("Selection and copy completed!")

def move_back_to_home():
    print("Moving back to home...")
    chrome_location = locate_image('./img/chrome.png')
    if not chrome_location:
        print("Chrome icon not found. Aborting.")
        return
    
    chrome_x, chrome_y = chrome_location
    pyautogui.moveTo(chrome_x, chrome_y)
    time.sleep(CONFIG['click_delay'])
    pyautogui.moveTo(100, 10)
    time.sleep(CONFIG['click_delay'])
    pyautogui.click()
    time.sleep(CONFIG['click_delay'])
    pyautogui.moveRel(400, 400)
    pyautogui.click()
    next_location = locate_image('./img/next.png')
    if not next_location:
        print("Next button not found. Aborting.")
        return
    
    next_x, next_y = next_location
    pyautogui.moveTo(next_x, next_y)
    pyautogui.click()

def check_status(count=1):
    location = locate_image('./img/voice.png', confidence=0.9, attempts=1)
    if location:
        print('conversion completed')
        print("JSON conversion request sent!")
        move_back_to_home()
    else:
        print(f'is processing {count}')
        time.sleep(1)
        check_status(count + 1)

def cover_to_json():
    print("Converting cover to JSON with default instructions...")
    # Locate Chrome icon
    chrome_location = locate_image('./img/chrome.png')
    if not chrome_location:
        print("Chrome icon not found. Aborting.")
        return
    
    # Move to Chrome icon
    chrome_x, chrome_y = chrome_location
    pyautogui.moveTo(chrome_x, chrome_y)
    
    # Move relative to chrome icon position
    print("Moving relative to Chrome icon...")
    pyautogui.moveRel(300, 0)
    
    # Click on the adjusted location
    pyautogui.click()
    time.sleep(CONFIG['click_delay'])
    
    # Locate entry point for pasting
    entry_location = locate_image('./img/ask.png')
    if not entry_location:
        print("Entry point not found. Aborting.")
        return
    
    # Move to entry location
    entry_x, entry_y = entry_location
    pyautogui.moveTo(entry_x, entry_y)
    
    # Move relative to entry position
    print("Moving relative to entry point...")
    pyautogui.moveRel(0, -10)
    
    # Click and type default text
    pyautogui.click()
    time.sleep(CONFIG['click_delay'])
    
    # Type the default text first
    print("Typing default instructions text...")
    
    # Put the default text in clipboard first (temporarily)
    original_clipboard = pyperclip.paste()  # Save current clipboard
    pyperclip.copy(DEFAULT_TEXT)
    
    # Paste the default text
    if IS_MAC:
        pyautogui.hotkey('command', 'v')
    else:
        pyautogui.hotkey('ctrl', 'v')
    
    time.sleep(CONFIG['click_delay'])
    pyautogui.keyDown('shift')
    pyautogui.press('enter')  # Add a line break between instructions and data
    pyautogui.press('enter')  # Add another line break for clarity
    pyautogui.keyUp('shift')
    time.sleep(CONFIG['click_delay'])
    
    # Put the original copied content back to clipboard
    pyperclip.copy(original_clipboard)
    
    # Now paste the original copied content (the data to be converted)
    print("Pasting clipboard content (data)...")
    if IS_MAC:
        pyautogui.hotkey('command', 'v')
    else:
        pyautogui.hotkey('ctrl', 'v')
    
    print("Default instructions and data pasting completed!")
    
    # Look for send button
    send_location = locate_image('./img/send.png', confidence=0.9)
    if not send_location:
        print("Send button not found. Aborting. Wait for 5 seconds and check again ")
        time.sleep(5)
        cover_to_json()
        return
    
    # Move to send button and click
    send_x, send_y = send_location
    pyautogui.moveTo(send_x, send_y)
    pyautogui.click()
    time.sleep(3)

    pyautogui.moveRel(0, -200)

    check_status()

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
    
    # Scroll to bottom and then search for the target image while scrolling up
    scroll_to_bottom()
    
    # Find the target image by scrolling up continuously until found
    start_coords = scroll_up_until_found(target_image_path)
    if not start_coords:
        print("Target image could not be found after scrolling up. Aborting.")
        return
    
    # Configure the end selection point
    end_selector = {
        'image_path': searchbar_image_path,
        'confidence': CONFIG['search_confidence'],
        'attempts': 5,
        'offset_y': 140  # 140px below search bar
    }
    
    # Perform the selection and copy
    select_and_copy_content(start_coords, end_selector)
    
    # Operation completed
    print("Operation completed successfully!")

    cover_to_json()

if __name__ == "__main__":
    # Check platform and print info
    print(f"Running on platform: {platform.system()}")
    
    # Run the function in a loop 50 times
    print("Starting scroll, select, and copy operation...")
    
    for iteration in range(1, 51):
        print(f"\n{'='*50}")
        print(f"Starting iteration {iteration} of 50")
        print(f"{'='*50}\n")
        
        scroll_select_and_copy()
        
        # If we want to add a delay between iterations, uncomment this:
        # if iteration < 50:
        #     delay = 2  # Seconds delay between iterations
        #     print(f"\nCompleted iteration {iteration}. Waiting {delay} seconds before next iteration...\n")
        #     time.sleep(delay)
        # else:
        #     print(f"\nAll 50 iterations completed successfully!")