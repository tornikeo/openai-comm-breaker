from dotenv import dotenv_values
import os
import openai

def assure_ends_with_dot(prompt):
    prompt = prompt.strip().replace('.','')
    prompt = prompt + '.' if prompt[-1] != '.' else prompt
    return prompt


import sys
import time
import threading
import inquirer
from gtts import gTTS
import vlc
import base64
import playsound
import time

class Spinner:
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1: 
            for cursor in '|/-\\': yield cursor

    def __init__(self, delay=0.2):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def __enter__(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def __exit__(self, exception, value, tb):
        self.busy = False
        time.sleep(self.delay)
        if exception is not None:
            return False

def get_at_most(s,n):
  try:
    return s[:n] + f'... truncated, {len(s)} characters left.'
  except:
    return s

def main():
  os.makedirs('speech', exist_ok=True)
  config = dotenv_values(".env")
  openai.api_key = config['OPENAI_API_KEY']
  while True:
    prompt = input('Enter your text: ')

    print('Waiting for OpenAI response...')
    with Spinner():
      response = openai.Edit.create(
        engine="text-davinci-edit-001",
        input=prompt,
        instruction="Paraphrase extremely verbosely.",
        temperature=1,
        top_p=1,
        n=3,
      )
    texts = []
    for choice in response['choices']:
        if 'text' in choice.keys():
            texts.append(choice['text'].strip().encode("ascii", errors="ignore").decode())
    # for i, text in enumerate(texts):
    #   print(str(i + 1) + ') ' + text)
    questions = [
      inquirer.List('choice',
                    message="Select one generated response",
                    choices=[get_at_most(text, 300) for text in texts],
                ),
    ]
    choice = inquirer.prompt(questions)['choice']
    # choice = "Something is going on."
    print('Generating speech...')
    with Spinner():
      output = gTTS(text=choice, lang='en', slow=True)
      file_name_string = "".join(x.lower() for x in choice if x.isalnum())
      file_name_string = file_name_string[:20] if len(file_name_string) > 20 else file_name_string
      file_path = f"speech/{file_name_string}.mp3"
      if os.path.exists(file_path):
        os.remove(file_path)
      output.save(file_path)
      time.sleep(3)

    print('Playing audio...')
    playsound.playsound(file_path, True)
    print('\n')


if __name__ == '__main__':
  main()