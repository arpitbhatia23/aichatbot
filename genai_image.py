from google import genai
from google.genai import types
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image
import os
load_dotenv()
api_key=os.getenv("api_key")
client=genai.Client(api_key=api_key)

def gen_image():
    print("🤖 : which type of image in can create for you")
    while True:
        user_input=input("👦 : ")
        if user_input.lower().strip()=="exit":
            break
        response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=user_input,
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE']
        )
        )

        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print("🤖 : ",part.text)
            elif part.inline_data is not None:
                image = Image.open(BytesIO((part.inline_data.data)))
                image.save('gemini-native-image.png')
                image.show()


if __name__ == '__main__':
    gen_image()