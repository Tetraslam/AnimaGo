import torch
import torchaudio
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification
import sys
import os
from pathlib import Path

class AudioDetector:
    def __init__(self):
        print("Loading audio classification model...")
        model_name = "MIT/ast-finetuned-audioset-10-10-0.4593"
        
        try:
            self.feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
            self.model = AutoModelForAudioClassification.from_pretrained(model_name)
            self.model.eval()
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {e}")
            sys.exit(1)
        
        # Animal sound keywords to filter for
        self.animal_keywords = {
            'bird', 'chirp', 'tweet', 'cat', 'meow', 'dog', 'bark',
            'rooster', 'chicken', 'duck', 'goose', 'pig', 'horse',
            'cow', 'sheep', 'cricket', 'frog', 'snake', 'animal'
        }

    def detect_animal(self, audio_path):
        try:
            # Convert to absolute path and check if file exists
            audio_path = os.path.abspath(audio_path)
            if not os.path.exists(audio_path):
                print(f"Error: File not found: {audio_path}")
                return None, 0.0

            print(f"Loading audio file: {audio_path}")
            
            # Load and resample audio file
            try:
                waveform, sample_rate = torchaudio.load(audio_path)
            except Exception as e:
                print(f"Error loading audio file. Make sure it's a valid audio format (wav, mp3, etc).")
                print(f"Error details: {str(e)}")
                return None, 0.0
            
            # Convert to mono if stereo
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)
            
            # Resample if needed (model expects 16kHz)
            if sample_rate != 16000:
                resampler = torchaudio.transforms.Resample(sample_rate, 16000)
                waveform = resampler(waveform)
            
            # Extract features
            inputs = self.feature_extractor(
                waveform.squeeze().numpy(), 
                sampling_rate=16000, 
                return_tensors="pt"
            )
            
            # Run inference
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Get top prediction
            confidence, index = torch.max(predictions[0], dim=0)
            label = self.model.config.id2label[index.item()]
            confidence = confidence.item()
            
            # Check if it's an animal sound
            if any(keyword in label.lower() for keyword in self.animal_keywords):
                return label, confidence
            else:
                return None, 0.0
                
        except Exception as e:
            print(f"Error processing audio file: {e}")
            return None, 0.0

def main():
    if len(sys.argv) != 2:
        print("Usage: python audiodetector.py <audio_file>")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    
    # Try to find the file in different locations
    possible_paths = [
        audio_path,  # Direct path
        os.path.join(os.getcwd(), audio_path),  # Current directory
        os.path.join(os.getcwd(), 'src', 'services', audio_path),  # src/services directory
    ]
    
    file_found = False
    for path in possible_paths:
        if os.path.exists(path):
            audio_path = path
            file_found = True
            break
    
    if not file_found:
        print(f"\nError: Could not find audio file in any of these locations:")
        for path in possible_paths:
            print(f"- {path}")
        sys.exit(1)
    
    detector = AudioDetector()
    print(f"\nAnalyzing audio file: {audio_path}")
    label, confidence = detector.detect_animal(audio_path)
    
    if label:
        print(f"\nDetected animal sound: {label}")
        print(f"Confidence: {confidence*100:.1f}%")
    else:
        print("\nNo animal sounds detected with high confidence.")

if __name__ == "__main__":
    main()
