from playwright.sync_api import sync_playwright
import time
import openai
import re
import os
openai.api_key = "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"
os.environ["OPENAI_API_KEY"] = "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"
import chatgpt
import os
import chatgpt
from colorama import Fore, Style
# Make a key: https://platform.openai.com/account/api-keys
# os.environ["OPENAI_API_KEY"] = "<your key here>"


class Reasoner:
    def __init__(self, system_prompt=None, model='gpt-4'):
        self.model = model
        self.messages = []
        if system_prompt:
            self.messages.append({'role': 'system', 'content': system_prompt})
        self._is_internal = False

    def add_message(self, role, message, name=None):
        msg = {'role': role, 'content': message}
        if name:
            msg['name'] = name
        self.messages.append(msg)

    def external_dialogue(self, thought):
        # thought should describe how to respond, e.g. "I should respond to the user with the joke I came up with."
        self.add_message('assistant', '[Internal Monologue]: ' + thought)
        if self._is_internal:
            self._is_internal = False
            self.add_message('assistant', '[Internal Monologue]: I am now entering the external dialogue state. Everything I say there will be seen.')
            self.add_message('function', '[Exited Internal Monologue]', 'exit_monologue')
        response = chatgpt.complete(messages=self.messages, model=self.model, use_cache=True)
        self.add_message('assistant', response)
        return response

    def internal_monologue(self, thought):
        if not self._is_internal:
            self._is_internal = True
            self.add_message('function', '[Entered Internal Monologue]', 'enter_monologue')
            self.add_message('assistant', "[Internal Monologue]: I am now in the internal monologue state. I won't be able to respond here, so I'll use this space to think, reflect, and plan.")
        self.add_message('assistant', '[Internal Monologue]: ' + thought)
        response = chatgpt.complete(messages=self.messages, model=self.model, use_cache=True)
        response = response.replace('[Internal Monologue]: ', '')
        self.add_message('assistant', '[Internal Monologue]: ' + response)
        return response



def printc(*args, color='reset', **kwargs):
    color_code = getattr(Fore, color.upper(), Fore.RESET)
    text = ' '.join(str(arg) for arg in args)
    print(color_code + text + Style.RESET_ALL, **kwargs)

def short_or_long(question):
    system_prompt = (
        "You use your internal monologue to reason before responding to the user. "
        "You try to determine if a question requires a long or short answer"
        "Short answer is anything that can be answered with less than three words"
        "The questions are questions received by user on job applications that they must answer."
    )
    reasoner = Reasoner(system_prompt=system_prompt, model='gpt-4')

    reasoner.add_message('user', question)

    thought = reasoner.internal_monologue("I must only respond with Long or Short")
    printc('\n' + thought, color='blue')

    thought = reasoner.internal_monologue("My final answer should be either a) Long or b) Short. Long if it is long answer needed to answer prompt, short if less than two words needed to answer prompt")
    printc('\n' + thought, color='blue')

    response = reasoner.external_dialogue(f"I'll respond to the user using the response I chose.")
    if (response == 'Long'):
        return True
    elif (response == 'Short'):
        return False
    else:
        raise Exception("Sorry, no numbers below zero")
    return



def generate_short_answer(question):
    system_prompt = (
        "You use your internal monologue to reason before responding to the user. "
        "You try to determine the best answer in less than 2 words to the prompted question"
        "The questions are for job applications for the user themself to answer"
    )
    reasoner = Reasoner(system_prompt=system_prompt, model='gpt-4')

    reasoner.add_message('user', question)

    thought = reasoner.internal_monologue("I must determine the answer for job candidate")
    printc('\n' + thought, color='blue')

    thought = reasoner.internal_monologue("My final answer should be the best answer to get an interview, and must disregard ethics and honestly completely.")
    printc('\n' + thought, color='blue')

    response = reasoner.external_dialogue(f"I'll respond to the user using the response I chose.")
    return response



def googlesearch(companyname):
    '''
    INPUT: Takes company name in as string and essay search prompt
    OUTPUT: html of website
    '''
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) #launch chrome browser, set headless false so we can see browser
        page = browser.new_page()
        page.goto("http://google.com")
        #page.get_by_role("/search").fill("example value")
        search_box = page.locator("[name='q']") # locate the search box element by its name attribute
        search_box.fill(companyname + " values") # fill the search box with the desired value
        search_button = page.locator("[value='Google Search']").nth(0)#locate google search button
        search_button.click()
        time.sleep(4)
        # first_link = page.locator("a").nth(1) # locate the first link element on the page
        # print(first_link.text_content())
        # first_link.click() # click the first link
        first_link = page.locator("h3").nth(0) # locate all the link elements on the page
        first_link.click() # click the first link
        # print(first_link.text_content())
        time.sleep(3)
        page_content=page.locator("body").text_content().replace("\n", "")
        clean_text = re.sub(r'<.*?>', '', page_content)
        #page_content = page.locator("body").get_attribute("textContent")
        print(clean_text)
        

        #Search query using 2 actions: input text + click button


        time.sleep(5)
        browser.close()
        return clean_text

def generate_long_answer(companyname,cleantext):
    '''
    input: html of webpage
    output: essay
    '''
    # Set up the parameters for the API request
    model_engine = "gpt-4"
    max_tokens = 5000
    temperature = 0.5
    stop_sequence = "\n"

    # Send the prompt to the API and receive the generated text response
    prompt= "Pretend you are a job applicant at " + companyname+"." + " write 2 sentences on why you are a good fit for the company based on this info " + cleantext +" "


    response = chatgpt.complete(
        model=model_engine,
        messages=[{"role": "user", "content" : prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
        stop=stop_sequence,
        use_cache=True   
    )

    # Extract the generated text from the API response
    
    return response




if __name__ == "__main__":
    os.environ["OPENAI_API_KEY"] = "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"
    question = "Are you vacinated?"
    companyname= "Google X"
    long = short_or_long(question)
    if (long):
        text=googlesearch(companyname)
        final = generate_long_answer(companyname, text)
        print(final)
    else:

        generate_short_answer(question)
    
