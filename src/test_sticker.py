from services.sticker import extract_animal
import os

def main():
    # Get the absolute path to the test image
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_image = os.path.join(current_dir, "services", "IMG_2231.jpg")
    
    if not os.path.exists(test_image):
        print(f"Test image not found at {test_image}")
        return
        
    print(f"Processing image: {test_image}")
    try:
        output_path = extract_animal(test_image)
        print(f"Saved extracted image to: {output_path}")
    except Exception as e:
        print(f"Error processing image: {str(e)}")

if __name__ == "__main__":
    main()
