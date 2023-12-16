Chloe is a telegram chat bot using ChatGPT (and soon Gemini)

This is the Python implement of [Chloe](https://github.com/DiamondGo/chloe) ChatBot. The Golang version is discontinued because of lack of API support.

You can talk to her 1 on 1 or in group chat. In group chat you need to name her at the beginning of your question or @ her bot username.

Please change conf/config.yml and put your own keys there.

You need to get 2 things done to make this work:
* An OpenAI apikey: get one free at https://platform.openai.com/account .
* A telegram bot: send /newbot to BotFather on telegram.

# Run the ChatBot

There are two ways to run this app.

## 1. Run with shell command:
```bash
# python 3.7 or later (early version may also work)
pip install -r requirements.txt # install dependencies
python main.py
```

## 2. Run within docker(simple and recommended)
```bash
# make sure you have docker and docker-compose installed
cd ./docker
docker-compose up --no-start && docker-compose start
```
  
Have fun!

Ask question in text:  
![ask question in text](https://github.com/DiamondGo/blob/blob/chloe/ask_coding.jpg?raw=true)


Ask question in voice(if you want a reply in voice you need to setup pyservice localy):  
![ask question in text](https://github.com/DiamondGo/blob/blob/chloe/tts.jpg?raw=true)

Draw picture(Dall-e 2):  
![ask question in text](https://github.com/DiamondGo/blob/blob/chloe/draw_pic.jpg?raw=true)

Ask question about picture(Vision)
![ask question in text](https://github.com/DiamondGo/blob/blob/chloe/drug_question.png?raw=true)