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
    'scroll_down_amount': -400,   # Amount to scroll down (negative)
    'scroll_up_amount': 400,      # Amount to scroll up (positive)
}

# Default text to paste before the copied content
DEFAULT_TEXT = """Please convert the following Bible text from a regional language into JSON format. 
Make sure you:
1) Detect each verse number strictly.
2) Keep verses sequential.
3) Avoid merging verse texts.
4) Preserve all text details.


Context:
- The format for the book name and chapter number will be like "THAUREYMEI 1," where:
  - "THAUREYMEI" is the book name.
  - "1" is the chapter number.
- The book names may vary (e.g., "THAUREYMEI," "GENESIS," etc.), so ensure that each book name is treated uniquely to avoid misidentification.
- The regional language text should follow this structure: 
  - Book Name, Chapter Number (e.g., "THAUREYMEI 1").
  - Verses should be split by numbers, and each verse will be in the format "1", "2", "3", etc., followed by the verse text.


Book Name: "THAUREYMEI"
Chapter: {chapter_number}
Slug: "thaureymei"
Language Name: "ruanglat"
Language Code: "rongbsi"

Expected JSON Format:
{{
  "book": "THAUREYMEI",
  "slug": "thaureymei",
  "chapter": {chapter_number},
  "languageName": "ruanglat",
  "languageCode": "rongbsi",
  "content": [
    {{ "heading": "Mbaanv Damhmei Pary" }},
    {{ "1": "Thaurey khou, Ravguangc rui tingpuk lev kandih damclou khwan e." }},
    {{ "2": "Mi ganv khou tei kalwn maekna khatni nsa karaeng bam khwan e..." }}
    ...
  ]
}}

Do not stop until all the text is converted to json and don't ask me "would like like to continue or do this and then until all the text is converted" 

Text to Convert:

"""

def find_image_on_screen(image_path, confidence=None, attempts=10, scroll_amount=100):
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
    
    for attempt in range(attempts):
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                return pyautogui.center(location)
        except Exception as e:
            print('----')
        
        # If image not found and we have more attempts, scroll and try again
        if attempt < attempts - 1:
            pyautogui.scroll(scroll_amount)
            time.sleep(CONFIG['scroll_delay'])
    
    return None

def scroll_to_page_bottom(num_scrolls=20):
    """Scroll to the bottom of the page"""
    print("Scrolling to the bottom of the page...")
    for _ in range(num_scrolls):
        pyautogui.scroll(CONFIG['scroll_down_amount'])
        time.sleep(CONFIG['scroll_delay'])

def scroll_up_and_find_target(target_image_path, max_scrolls=30, scroll_amount=400):
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
        target_coords = find_image_on_screen(
            target_image_path, 
            confidence=CONFIG['search_confidence'],
            attempts=1,  # Just one attempt per scroll
            scroll_amount=0  # Don't scroll inside find_image_on_screen
        )
        
        if target_coords:
            print(f"Target image found after {scroll_count} scrolls")
            # Scroll one more time
            print("Scrolling one more time as requested")
            pyautogui.scroll(scroll_amount)
            time.sleep(CONFIG['scroll_delay'])
            
            # Now find the image again at its new position
            new_target_coords = find_image_on_screen(
                target_image_path,
                confidence=CONFIG['search_confidence'],
                attempts=3,  # Try a few times to find it in the new position
                scroll_amount=0
            )
            
            if new_target_coords:
                print(f"Target image found at new position after extra scroll")
                return new_target_coords
            else:
                print(f"Target image not found after extra scroll, using original coordinates")
                return target_coords
        
        # Not found, scroll up and try again
        print(f"Scroll up attempt {scroll_count + 1}/{max_scrolls}")
        pyautogui.scroll(scroll_amount)  # Positive for up
        time.sleep(CONFIG['scroll_delay'])
    
    print(f"Target image not found after {max_scrolls} scroll attempts")
    return None

def scroll_down_and_find_target(target_image_path, max_scrolls=50, scroll_amount=None):
    """
    Scroll down while checking for target image after each scroll
    
    Args:
        target_image_path (str): Path to the image to look for
        max_scrolls (int): Maximum number of scrolls to attempt
        scroll_amount (int): Amount to scroll down each time (negative value)
        
    Returns:
        tuple: (x, y) coordinates of found image, or None if not found after max_scrolls
    """
    print(f"Scrolling down while looking for {target_image_path}...")
    
    # Check if the image is already visible before scrolling
    target_coords = find_image_on_screen(
        target_image_path, 
        confidence=CONFIG['search_confidence'],
        attempts=1,
        scroll_amount=0
    )
    
    if target_coords:
        print(f"Target image already visible, no need to scroll")
        return target_coords
    
    scroll_amount = scroll_amount or CONFIG['scroll_down_amount']
    
    for scroll_count in range(max_scrolls):
        # Scroll down
        print(f"Scroll down attempt {scroll_count + 1}/{max_scrolls}")
        pyautogui.scroll(scroll_amount)  # Negative for down
        time.sleep(CONFIG['scroll_delay'])
        
        # Check for image after scrolling
        target_coords = find_image_on_screen(
            target_image_path, 
            confidence=CONFIG['search_confidence'],
            attempts=1,  # Just one attempt per scroll
            scroll_amount=0  # Don't scroll inside find_image_on_screen
        )
        
        if target_coords:
            print(f"Target image found after {scroll_count + 1} scrolls")
            return target_coords
    
    print(f"Target image not found after {max_scrolls} scroll attempts")
    return None

def select_and_copy_bible_content(start_coords, end_selector=None, default_end_y=10):
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
        end_coords = find_image_on_screen(
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

def navigate_to_next_chapter():
    print("Navigating to the next chapter...")
    chrome_location = find_image_on_screen('./img/chrome.png')
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
    next_location = find_image_on_screen('./img/next.png')
    if not next_location:
        print("Next button not found. Aborting.")
        return
    
    next_x, next_y = next_location
    pyautogui.moveTo(next_x, next_y)
    pyautogui.click()

def check_conversion_status(count=1, chapter_number=1):
    """Check if the conversion is complete and save the JSON file"""
    print(f"Checking conversion status (attempt {count})...")
    
    voice_found = False
    
    # Keep searching for voice.png until found while scrolling up
    while not voice_found:
        # Look for voice.png while scrolling up
        voice_coords = find_image_on_screen('./img/voice.png', confidence=0.95, attempts=1)
        if voice_coords:
            print("Voice icon found! Conversion is complete.")
            voice_found = True
            break
            
        # If not found, scroll up and continue searching
        print(f"Voice icon not found, scrolling up (attempt {count})...")
        pyautogui.scroll(CONFIG['scroll_down_amount'])  # Positive value for scrolling up
        time.sleep(2)
        count += 1
    
    # Only proceed with copy and save operations after voice.png is found
    if voice_found:
        # Now look for the copy button
        print("Looking for copy button...")
        copy_coords = find_image_on_screen('./img/copy.png', attempts=5)
        if copy_coords:
            print("Copy button found, clicking it...")
            pyautogui.moveTo(copy_coords)
            pyautogui.click()
            time.sleep(CONFIG['click_delay'])
        else:
            print("Could not find copy button!")
            return False
        
        # Look for books/genesis.png to save the JSON
        print("Looking for books icon...")
        books_coords = find_image_on_screen('./img/books/genesis.png', attempts=5)
        if books_coords:
            print("Books icon found, right-clicking it...")
            pyautogui.moveTo(books_coords)
            pyautogui.rightClick()
            time.sleep(CONFIG['click_delay'])
            
            # Move relative to right-click position and click
            pyautogui.moveRel(20, 20)
            pyautogui.click()
            time.sleep(CONFIG['click_delay'])
            
            # Type the chapter number with .json extension
            chapter_text = f"{chapter_number}.json"
            pyautogui.write(chapter_text)
            pyautogui.press('enter')
            time.sleep(CONFIG['click_delay'])
            
            print(f"Successfully saved chapter {chapter_number} as JSON!")

            time.sleep(CONFIG['click_delay'])
            if IS_MAC:
                pyautogui.hotkey('command', 'v')
                time.sleep(CONFIG['click_delay'])
                pyautogui.hotkey('command', 's')
            else:
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(CONFIG['click_delay'])
                pyautogui.hotkey('ctrl', 's')
            
            time.sleep(CONFIG['click_delay'])
            navigate_to_next_chapter()
            return True
        else:
            print("Could not find books icon!")
            return False

def convert_bible_text_to_json(chapter_number):
    print(f"Converting Bible chapter {chapter_number} to JSON...")
    # Locate Chrome icon
    chrome_location = find_image_on_screen('./img/chrome.png')
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
    entry_location = find_image_on_screen('./img/ask.png')
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
    
    # Format default text with chapter number
    formatted_text = DEFAULT_TEXT.format(chapter_number=chapter_number)
    
    # Put the default text in clipboard first (temporarily)
    original_clipboard = pyperclip.paste()  # Save current clipboard
    pyperclip.copy(formatted_text)
    
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
    
    print("Instructions and data pasted successfully!")
    
    # Look for send button
    send_location = find_image_on_screen('./img/send.png', confidence=0.9)
    if not send_location:
        print("Send button not found. Retrying in 5 seconds...")
        time.sleep(5)
        convert_bible_text_to_json(chapter_number)
        return
    
    # Move to send button and click
    send_x, send_y = send_location
    pyautogui.moveTo(send_x, send_y)
    pyautogui.click()
    time.sleep(3)

    pyautogui.moveRel(0, -200)

    check_conversion_status(chapter_number=chapter_number)

def process_bible_chapter(
    chapter_number,
    target_image_path='./img/rnr.png', 
    searchbar_image_path='./img/searchbar.png', 
    preparation_delay=0
):
    """
    Main function to process a single Bible chapter by scrolling, selecting content, and copying.
    
    Args:
        chapter_number (int): Current chapter number
        target_image_path (str): Path to the target image that marks start of selection
        searchbar_image_path (str): Path to the search bar image
        preparation_delay (int): Initial delay to switch to browser
    """
    # Give time to switch to the browser window
    print(f"Switching to browser in {preparation_delay} seconds...")
    time.sleep(preparation_delay)
    
    # Try to find YouVersion indicator to confirm we're on the right page
    youversion_coords = find_image_on_screen('./img/youVersion.png')
    if youversion_coords:
        pyautogui.moveTo(youversion_coords, duration=1)
    else:
        print("Warning: YouVersion indicator not found. Make sure you're on the correct page.")
    
    # Find the target image by scrolling down until found
    start_coords = scroll_down_and_find_target(target_image_path)
    if not start_coords:
        print("Target image could not be found after scrolling down. Aborting.")
        return
    
    # Configure the end selection point
    end_selector = {
        'image_path': searchbar_image_path,
        'confidence': CONFIG['search_confidence'],
        'attempts': 5,
        'offset_y': 140  # 140px below search bar
    }
    
    # Perform the selection and copy
    select_and_copy_bible_content(start_coords, end_selector)
    
    # Operation completed
    print("Content selection completed successfully!")

    convert_bible_text_to_json(chapter_number)

if __name__ == "__main__":
    # Check platform and print info
    print(f"Running on platform: {platform.system()}")
    
    # Get the total number of chapters and current chapter
    try:
        total_chapters = int(input("Enter the total number of chapters to process: "))
        if total_chapters <= 0:
            print("Number must be positive. Setting to 1.")
            total_chapters = 1
            
        current_chapter = int(input(f"Enter the current chapter (1-{total_chapters}): "))
        if current_chapter <= 0 or current_chapter > total_chapters:
            print(f"Chapter must be between 1 and {total_chapters}. Setting to 1.")
            current_chapter = 1
    except ValueError:
        print("Invalid input. Setting to process chapter 1 of 1.")
        total_chapters = 1
        current_chapter = 1
    
    # Calculate remaining chapters
    remaining_chapters = total_chapters - current_chapter + 1
    
    print(f"\n{'='*50}")
    print(f"Starting Bible conversion process")
    print(f"Total chapters: {total_chapters}")
    print(f"Starting at chapter: {current_chapter}")
    print(f"Chapters to process: {remaining_chapters}")
    print(f"{'='*50}\n")
    
    # Process each chapter in sequence
    for chapter_idx in range(current_chapter, total_chapters + 1):
        print(f"\n{'='*50}")
        print(f"Processing chapter {chapter_idx} of {total_chapters}")
        print(f"{'='*50}\n")
        
        process_bible_chapter(chapter_number=chapter_idx)
        
        if chapter_idx < total_chapters:
            print(f"\nCompleted chapter {chapter_idx}. Moving to next chapter...\n")
            # Add a small delay before processing next chapter
            # time.sleep()
        else:
            print(f"\nAll chapters completed successfully!")