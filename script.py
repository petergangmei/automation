import pyautogui
import time

def scroll_select_and_copy():
    # Give some time to switch to the browser window
    print("Switching to browser in 3 seconds...")
    time.sleep(3)
    
    # Scroll to the bottom of the page
    print("Scrolling to the bottom of the page...")
    # PyAutoGUI scrolls in increments - negative values scroll down
    # We'll scroll multiple times to ensure we reach the bottom
    for _ in range(20):  # Adjust this number based on your page length
        pyautogui.scroll(-500)  # Scroll down
        time.sleep(0.2)  # Small delay between scrolls
    
    # Scroll up by a certain amount
    print("Scrolling up by a certain amount...")
    scroll_up_amount = 5  # Adjust this number as needed
    for _ in range(scroll_up_amount):
        pyautogui.scroll(400)  # Positive values scroll up
        time.sleep(0.2)
    
    # Look for the target image
    print("Looking for the target image...")
    target_image_location = None
    
    # Try finding the image multiple times while scrolling slightly
    search_attempts = 10
    for attempt in range(search_attempts):
        try:
            target_image_location = pyautogui.locateOnScreen('./img/rnr.png', confidence=0.8)
            if target_image_location:
                print(f"Image found at: {target_image_location}")
                break
        except Exception as e:
            print(f"Search attempt {attempt+1}: {e}")
        
        # If image not found, scroll slightly and try again
        if attempt < search_attempts - 1:
            pyautogui.scroll(100)  # Scroll up a bit
            time.sleep(0.5)
    
    if not target_image_location:
        print("Target image could not be found. Aborting.")
        return
    
    # Get the center coordinates of the found image
    target_x, target_y = pyautogui.center(target_image_location)
    
    # Scroll up by 50 from the image location
    print("Scrolling up by 50 from the image location...")
    pyautogui.scroll(50)
    time.sleep(0.5)
    
    # Click at the found position (adjusted for the scroll)
    adjusted_y = target_y - 10  # Adjust y position for the scroll up
    print(f"Clicking at position: ({target_x}, {adjusted_y})")
    pyautogui.click(target_x, adjusted_y)
    
    # Press and hold the mouse button to start selection
    print("Starting selection and scrolling to top...")
    pyautogui.mouseDown(target_x, adjusted_y)
    time.sleep(0.5)  # Small delay to ensure the click registers
    
    # Scroll to the top while holding the mouse button
    for _ in range(30):  # Adjust based on page length
        pyautogui.scroll(500)  # Scroll up
        time.sleep(0.2)
    
    # Look for the search bar at the top
    print("Looking for the search bar...")
    searchbar_location = None
    
    # Try finding the searchbar image multiple times
    search_attempts = 5
    for attempt in range(search_attempts):
        try:
            searchbar_location = pyautogui.locateOnScreen('./img/searchbar.png', confidence=0.8)
            if searchbar_location:
                print(f"Search bar found at: {searchbar_location}")
                break
        except Exception as e:
            print(f"Search bar search attempt {attempt+1}: {e}")
        
        # If searchbar not found, small delay and try again
        time.sleep(0.5)
    
    if not searchbar_location:
        print("Search bar could not be found. Using default top position.")
        # Move to a default top position if search bar isn't found
        top_x, top_y = target_x, 10
    else:
        # Get the center coordinates of the found search bar
        searchbar_x, searchbar_y = pyautogui.center(searchbar_location)
        # Move to 100 pixels below the search bar
        top_x, top_y = searchbar_x, searchbar_y + 130
        print(f"Using position 100px below search bar: ({top_x}, {top_y})")
    
    # Move to the determined position to complete the selection
    pyautogui.moveTo(top_x, top_y, duration=1)
    
    # Release the mouse button to complete the selection
    pyautogui.mouseUp()
    
    # Copy the selected text
    print("Copying selected text...")
    pyautogui.hotkey('ctrl', 'c')  # Use 'command', 'c' for Mac
    
    print("Operation completed!")
    
    # Optional: If you want to access the copied text
    # You would need to use a clipboard module like 'pyperclip'
    # import pyperclip
    # copied_text = pyperclip.paste()
    # print(f"Copied text: {copied_text}")

if __name__ == "__main__":
    # Run the function
    print("Starting scroll, select, and copy operation...")
    scroll_select_and_copy()